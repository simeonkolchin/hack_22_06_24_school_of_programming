import tracemalloc
import sys
import os
import asyncio
import tempfile
import uuid
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import Message, ContentType, FSInputFile
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart
from aiogram import F
import pandas as pd
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from PIL import Image, ImageDraw
import io

import time

# Включение отслеживания распределения памяти
tracemalloc.start()

# Добавление корневой директории в системный путь
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))
sys.path.append(project_root)

from app.ml.ml import LogoErrorChecker
from app.bot.sql_lite import create_db, add_photo  # Импорт функции добавления фото в базу данных
from app.bot.yandex_disk import upload_to_yandex_disk  # Импорт функции загрузки фото на Яндекс.Диск

# Токен вашего бота
API_TOKEN = '7207561115:AAEMfuR0dRTIfQT3jxLk_yGxskAqMBEBaJQ'
# API_TOKEN = '6804881734:AAGdFi4mJBnubRLNtfP5ALKCnxqpK_nITRA'

# Инициализация бота, диспетчера и хранилища
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# Инициализация объекта для проверки ошибок логотипа
checker = LogoErrorChecker()

create_db()

# Загрузка данных из Excel
def load_data(file_path):
    df = pd.read_excel(file_path)
    regions = df['Регион'].unique().tolist()
    object_types = df['Тип объекта'].unique().tolist()
    addresses = df[['Регион', 'Тип объекта', 'Населенный пункт', 'Улица', 'Дом']].to_dict(orient='records')
    return df, regions, object_types, addresses

df, regions, object_types, addresses = load_data('app/bot/files/Перечень_объектов_брендирования_Тюменской_области_с_адресами.xlsx')

class main_state(StatesGroup):
    waiting_for_region = State()
    waiting_for_object_type = State()
    waiting_for_address = State()

@router.message(CommandStart())
async def send_welcome(message: Message):
    """
    Обработчик команды /start. Приветствует пользователя.
    """
    await message.answer("Добро пожаловать в бот для проверки ошибок логотипа! Отправьте изображение, чтобы начать работу.")

@router.message(F.content_type == ContentType.PHOTO)
async def handle_image(message: Message, state: FSMContext):
    """
    Обработчик сообщений с изображениями. Выполняет проверку логотипов на изображении.
    """
    photo = message.photo[-1]
    photo_file = await bot.get_file(photo.file_id)
    photo_bytes = await bot.download_file(photo_file.file_path)

    photo_bytes = photo_bytes.getvalue()
    image = Image.open(io.BytesIO(photo_bytes)).convert('RGB')

    # Проверка изображения на ошибки логотипов
    result = checker.check_errors(image)

    start = time.time()

    if result['people']:
        await message.answer("Присутствуют люди на фото")

    if not result['bbox_results']:
        await message.answer("Логотипы на изображении не распознаны.")
        return

    # Формирование и отправка результата
    error = 0
    draw = ImageDraw.Draw(image)
    caption = ""
    for idx, bbox_result in enumerate(result['bbox_results']):
        # Отметка обнаруженных логотипов на изображении
        bbox = bbox_result['bbox']
        if isinstance(bbox, (list, tuple)) and len(bbox) >= 4:
            bbox = tuple(map(int, bbox[:4]))
            draw.rectangle(bbox, outline="red", width=2)

        # Сохранение временного файла с отмеченными логотипами
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            image.save(tmp_file, format='PNG')
            tmp_file_path = tmp_file.name

        # Отчет по изображению
        caption += f"<b>Логотип {idx + 1}:</b>\n"

        for error in bbox_result['errors']:
            caption += error + "\n"

        for info in bbox_result['info']:
            caption += info + "\n"

    await message.answer_photo(FSInputFile(tmp_file_path), caption=caption, parse_mode="HTML")

    if error:
        os.remove(tmp_file_path)
        return

    await state.update_data(tmp_file_path=tmp_file_path)
    await state.update_data(result=result)
    await state.update_data(photo_bytes=photo_bytes)

    region_message = "Фотография была корректна определена. Чтобы ее сохранить, выберите субъект РФ (кроме субъекта с типом «nan»):\n" + "\n".join(
        [f"{i + 1}. {region}" for i, region in enumerate(regions)])
    await message.answer(region_message)
    await state.set_state(main_state.waiting_for_region)


@router.message(main_state.waiting_for_region)
async def waiting_for_region(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await state.get_data()
    region_index = int(message.text.strip()) - 1
    if 1 <= region_index < len(regions):
        region = regions[region_index]
        user_data['region'] = region
        await state.update_data(region=region)
        
        object_type_message = "Выберите тип объекта (кроме объекта с типом «nan»):\n" + "\n".join(
            [f"{i + 1}. {object_type}" for i, object_type in enumerate(object_types)])
        await message.answer(object_type_message)
        await state.set_state(main_state.waiting_for_object_type)
    else:
        await message.answer("Некорректный выбор. Пожалуйста, выберите правильный номер субъекта РФ.")


@router.message(main_state.waiting_for_object_type)
async def waiting_for_object_type(message: Message, state: FSMContext):
    user_data = await state.get_data()
    object_type_index = int(message.text.strip()) - 1
    if 1 <= object_type_index < len(object_types):
        object_type = object_types[object_type_index]
        user_data['object_type'] = object_type
        await state.update_data(object_type=object_type)

        filtered_addresses = [
            f"{row['Населенный пункт']}, {row['Улица']}, {row['Дом']}"
            for _, row in df[(df['Регион'] == user_data['region']) & (df['Тип объекта'] == user_data['object_type'])].iterrows()
        ]
        address_message = "Выберите адрес объекта (кроме объекта с типом «nan»):\n" + "\n".join(
            [f"{i + 1}. {addr}" for i, addr in enumerate(filtered_addresses)])
        await message.answer(address_message)
        await state.set_state(main_state.waiting_for_address)
    else:
        await message.answer("Некорректный выбор. Пожалуйста, выберите правильный номер типа объекта.")


@router.message(main_state.waiting_for_address)
async def waiting_for_address(message: Message, state: FSMContext):
    user_data = await state.get_data()
    address_index = int(message.text.strip()) - 1
    
    filtered_addresses = [
        {
            'Населенный пункт': row['Населенный пункт'],
            'Улица': row['Улица'],
            'Дом': row['Дом'],
            'Global ID': row['Global ID']
        }
        for _, row in df[(df['Регион'] == user_data['region']) & (df['Тип объекта'] == user_data['object_type'])].iterrows()
    ]
    
    if 0 <= address_index < len(filtered_addresses):
        address_data = filtered_addresses[address_index]
        address = f"{address_data['Населенный пункт']}, {address_data['Улица']}, {address_data['Дом']}"
        user_data['address'] = address
        await state.update_data(address=address)
        
        global_id = str(int(address_data['Global ID']))
        await state.update_data(global_id=global_id)

        # Получение данных из промежуточного состояния
        tmp_file_path = user_data['tmp_file_path']
        result = user_data['result']

        national_project = result['bbox_results'][0]['class']
        errors = ', '.join(result['bbox_results'][0]['errors'])
        info = ', '.join(result['bbox_results'][0]['info'])
        
        # Сохранение фото на Яндекс.Диск
        photo_url = upload_to_yandex_disk(tmp_file_path, national_project, user_data['region'], user_data['object_type'], user_data['address'])

        # Сохранение информации в базу данных
        city, street, house = user_data['address'].split(', ', 2)
        add_photo(global_id, national_project, user_data['object_type'], user_data['region'], city, street, house, photo_url, errors, info)

        await message.answer(f"Фото успешно загружено и информация сохранена. \n\nGlobal ID: {global_id} \n\nНациональный проект: {national_project} \nТип объекта: {user_data['object_type']} \n\nРегион: {user_data['region']} \nГород: {city} \nУлица: {street} \nДом: {house} \n\nСсылка на Яндекс.Диск: <a href='{photo_url}'>НАЖМИ, ЧТОБЫ ПОСМОТРЕТЬ</a> \n\nОшибки: {errors if errors else 'Нет'} \n\nОбщая информация: {info}", parse_mode="HTML")
        
        # Удаление временного файла
        os.remove(tmp_file_path)
        
        # Очистка состояния
        await state.clear()
    else:
        await message.answer("Некорректный выбор. Пожалуйста, выберите правильный номер адреса объекта.")


async def run_bot():
    """
    Запуск бота.
    """
    dp.include_router(router)
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(run_bot())

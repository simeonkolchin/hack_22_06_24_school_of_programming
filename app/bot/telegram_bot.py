import tracemalloc
import sys
import os
import asyncio
import tempfile
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import Message, ContentType, FSInputFile
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart
from aiogram import F
from PIL import Image, ImageDraw
import io

# Включение отслеживания распределения памяти
tracemalloc.start()

# Добавление корневой директории в системный путь
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))
sys.path.append(project_root)

from app.ml.ml import LogoErrorChecker

# Токен вашего бота
API_TOKEN = '7207561115:AAEMfuR0dRTIfQT3jxLk_yGxskAqMBEBaJQ'

# Инициализация бота, диспетчера и хранилища
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# Инициализация объекта для проверки ошибок логотипа
checker = LogoErrorChecker()

@router.message(CommandStart())
async def send_welcome(message: Message):
    """
    Обработчик команды /start. Приветствует пользователя.
    """
    await message.answer("Добро пожаловать в бот для проверки ошибок логотипа! Отправьте изображение, чтобы начать работу.")

@router.message(F.content_type == ContentType.PHOTO)
async def handle_image(message: Message):
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

    if not result['bbox_results']:
        await message.answer("Логотипы на изображении не распознаны.")
        return

    # Формирование и отправка результата
    draw = ImageDraw.Draw(image)
    caption = "<b>Распознанные ошибки:</b>\n"
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

        # Отчет по избражению
        caption += f"<b>Логотип {idx + 1}:</b>\n"
        caption += f"  - <b><u>Название класса, полученное при обработке:</u></b> {'Определить не удалось' if bbox_result['cropped_class'] == 'None' else bbox_result['cropped_class']}\n"
        caption += f"  - <b><u>Ошибки:</u></b> {', '.join(bbox_result['errors']) if bbox_result['errors'] else 'Не найдено'}\n"
        caption += f"  - <b><u>Класс логотипа, определённый по буквам на логотипе:</u></b> {'Определить не удалось' if bbox_result['ocr_class'] is None else bbox_result['ocr_class']}\n"
        caption += f"  - <b><u>Класс логотипа, определённый по цвету:</u></b> {', '.join(bbox_result['color_class'])}\n\n"
    caption += f"<b><u>Общий класс, определённый по всему изображению с помощью OCR:</u></b> {result['ocr_class']}"

    await message.answer_photo(FSInputFile(tmp_file_path), caption=caption, parse_mode="HTML")

    os.remove(tmp_file_path)

async def run_bot():
    """
    Запуск бота.
    """
    dp.include_router(router)
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(run_bot())

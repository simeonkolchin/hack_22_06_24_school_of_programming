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

tracemalloc.start()

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))
sys.path.append(project_root)

from app.ml.ml import LogoErrorChecker

API_TOKEN = '7207561115:AAEMfuR0dRTIfQT3jxLk_yGxskAqMBEBaJQ'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

checker = LogoErrorChecker()

@router.message(CommandStart())
async def send_welcome(message: Message):
    await message.answer("Добро пожаловать в бот для проверки ошибок логотипа! Отправьте изображение, чтобы начать работу.")

@router.message(F.content_type == ContentType.PHOTO)
async def handle_image(message: Message):
    photo = message.photo[-1]
    photo_file = await bot.get_file(photo.file_id)
    photo_bytes = await bot.download_file(photo_file.file_path)

    photo_bytes = photo_bytes.getvalue()
    image = Image.open(io.BytesIO(photo_bytes)).convert('RGB')

    result = checker.check_errors(image)

    draw = ImageDraw.Draw(image)
    for bbox_result in result['bbox_results']:
        bbox = bbox_result['bbox']
        print(f"Drawing rectangle with coordinates: {bbox}")
        if isinstance(bbox, (list, tuple)) and len(bbox) >= 4:
            bbox = tuple(map(int, bbox[:4]))
            draw.rectangle(bbox, outline="red", width=2)

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        image.save(tmp_file, format='PNG')
        tmp_file_path = tmp_file.name

    caption = "Распознанные ошибки:\n" + "\n".join(result['errors']) + "\n\n"
    for idx, bbox_result in enumerate(result['bbox_results']):
        caption += f"Логотип {idx + 1}:\n"
        caption += f"  BBox: {bbox_result['bbox']}\n"
        caption += f"  Класс: {bbox_result['cropped_class']}\n"
        caption += f"  Ошибки: {', '.join(bbox_result['errors'])}\n"
        caption += f"  OCR: {bbox_result['ocr_class']}\n"
        caption += f"  Цвет: {bbox_result['color_class']}\n"
        caption += "\n"
    caption += f"OCR класс для всего изображения: {result['ocr_class']}"
    await message.answer_photo(FSInputFile(tmp_file_path), caption=caption)

    os.remove(tmp_file_path)

async def run_bot():
    dp.include_router(router)
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(run_bot())

import os
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import Message, ContentType
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart
from aiogram import F

from ml.ml import LogoErrorChecker
from PIL import Image
import io

API_TOKEN = '7207561115:AAEMfuR0dRTIfQT3jxLk_yGxskAqMBEBaJQ'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# Инициализация класса проверки ошибок
checker = LogoErrorChecker()

@router.message(CommandStart())
async def send_welcome(message: Message):
    await message.answer("Welcome to the Logo Error Checker Bot! Send an image to get started.")

@router.message(F.content_type == ContentType.PHOTO)
async def handle_image(message: Message):
    photo = message.photo[-1]
    photo_file = await bot.get_file(photo.file_id)
    photo_bytes = await bot.download_file(photo_file.file_path)
    
    image = Image.open(io.BytesIO(photo_bytes)).convert('RGB')
    image.save("temp.jpg")

    # Предсказание
    error_list = checker.check_errors("temp.jpg")
    os.remove("temp.jpg")
    
    if error_list:
        response = "Detected errors:\n" + "\n".join(error_list)
    else:
        response = "No errors detected."
    
    await message.answer(response)

def run_bot():
    dp.include_router(router)
    dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    run_bot()

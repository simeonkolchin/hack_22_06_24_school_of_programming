from fastapi import FastAPI, UploadFile, File
from ml.ml import LogoErrorChecker
from PIL import Image
import io
import os

app = FastAPI()

# Инициализация класса проверки ошибок
checker = LogoErrorChecker()

@app.post("/check_errors/")
async def check_errors(file: UploadFile = File(...)):
    image = Image.open(io.BytesIO(await file.read())).convert('RGB')
    image.save("temp.jpg")

    # Предсказание
    error_list = checker.check_errors("temp.jpg")
    os.remove("temp.jpg")
    
    return {"errors": error_list}

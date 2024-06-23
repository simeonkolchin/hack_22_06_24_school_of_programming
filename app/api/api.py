from fastapi import FastAPI, UploadFile, File
from ml.ml import LogoErrorChecker
from PIL import Image
import io

app = FastAPI()

# Инициализация класса проверки ошибок
checker = LogoErrorChecker(
    classification_model_path='path_to_classification_model.onnx',
    yolo_people_model_path='path_to_yolo_people_model.pt'
)

@app.post("/check_errors/")
async def check_errors(file: UploadFile = File(...)):
    image = Image.open(io.BytesIO(await file.read())).convert('RGB')
    image.save("temp.jpg")

    # Предсказание
    error_list = checker.check_errors("temp.jpg")
    os.remove("temp.jpg")
    
    return {"errors": error_list}

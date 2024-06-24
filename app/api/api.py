from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.ml.ml import LogoErrorChecker
from PIL import Image
import io
import tempfile
import os

app = FastAPI()

checker = LogoErrorChecker()

@app.post("/check_errors/")
async def check_errors(file: UploadFile = File(...)):
    """
    Принимает изображение в виде файла, проверяет его на наличие ошибок с использованием различных моделей и возвращает результат в формате JSON.

    Параметры:
    - file: UploadFile - загружаемый файл изображения, который нужно проверить.

    Возвращает:
    - JSONResponse: результат проверки изображения, включающий список ошибок и информацию о найденных логотипах.
    
    Пример ответа:
    {
        "errors": [],
        "ocr_class": "some_class",
        "bbox_results": [
            {
                "bbox": [36, 2, 313, 246],
                "cropped_class": "some_class",
                "errors": ["Неправильное направление"],
                "ocr_class": "some_class",
                "color_class": "some_color"
            }
        ]
    }

    Возможные ошибки:
    - HTTPException 500: если произошла ошибка при обработке изображения или выполнении модели.
    """
    try:
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data)).convert('RGB')

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            image.save(tmp_file, format='PNG')
            tmp_file_path = tmp_file.name

        result = checker.check_errors(image)
        os.remove(tmp_file_path)

        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

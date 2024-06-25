import onnxruntime as ort
import torchvision.transforms as transforms
from PIL import Image
import numpy as np

class DirectionClassificator:
    """
    Класс для выполнения классификации направлений с использованием модели ONNX.

    Атрибуты:
        onnx_session (ort.InferenceSession): Сессия ONNX Runtime для классификационной модели.
        input_name (str): Имя входного узла модели ONNX.
        output_name (str): Имя выходного узла модели ONNX.
        transform (transforms.Compose): Преобразования, применяемые к входному изображению.
    """
    def __init__(self, classification_model_path='app/ml/weights/classification_direction.onnx'): 
        """
        Инициализирует DirectionClassificator с указанным путем к модели.

        Аргументы:
            classification_model_path (str): Путь к классификационной модели ONNX.
        """

        self.onnx_session = ort.InferenceSession(classification_model_path)
        self.input_name = self.onnx_session.get_inputs()[0].name
        self.output_name = self.onnx_session.get_outputs()[0].name
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def predict(self, image):
        """
        Предсказывает направление на основании входного изображения.

        Аргументы:
            image (PIL.Image.Image): Входное изображение для классификации.

        Возвращает:
            float: Результат классификации.
        """
        image = self.transform(image).unsqueeze(0).numpy()
        outputs = self.onnx_session.run([self.output_name], {self.input_name: image})
        output = outputs[0][0][0]
        return output

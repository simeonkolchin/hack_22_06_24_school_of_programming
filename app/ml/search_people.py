from ultralytics import YOLO

class SearchPeople:
    """
    Класс для поиска людей на изображениях с использованием модели YOLO.

    Атрибуты:
        model (YOLO): Загруженная модель YOLO для обнаружения людей.
    """
    def __init__(self, model_path='app/ml/weights/search_people.pt'):
        self.model = YOLO(model_path)
    
    def detect(self, image_path):
        """
        Выполняет обнаружение людей на изображении.

        Аргументы:
            image_path (str): Путь к изображению.

        Возвращает:
            bool: True, если люди обнаружены, иначе False.
        """
        results = self.model(image_path, conf=0.1, verbose=False)
        if 0 in results[0].boxes.data[:, 5]:
            return True
        else:
            return False

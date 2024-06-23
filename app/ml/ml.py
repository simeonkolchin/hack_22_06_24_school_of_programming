from ml.classification_direction import ImageClassifierONNX
from ml.ocr import OCRModel
from ml.search_people import PeopleSearcher
from app.ml.logo_detector import YoloModel
from ml.classification_crop import CropClassificator
from easyocr import Reader

class LogoErrorChecker:
    def __init__(self, yolo_model_path):
        self.classifier = ImageClassifierONNX()
        self.ocr_model = Reader(['ru'], gpu=True)
        self.people_searcher = PeopleSearcher()
        self.crop_classificatior = CropClassificator()
        self.yolo_model = YoloModel(yolo_model_path)

    def check_errors(self, image_path):
        errors = []
        
        classification_result = self.classifier.predict(image_path)
        if classification_result < 0:
            errors.append("Ошибка отображения: логотип расположен неправильно или имеет деффект с размер")
        
        # YOLO для людей -------------------
        if not self.people_detector.detect_person(image_path):
            errors.append("Person detection error: no persons detected.")

        return errors
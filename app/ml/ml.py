from ml.classification_direction import ImageClassifierONNX
from ml.ocr import OCRModel
from ml.search_people import PeopleSearcher
from ml.yolo_model import YoloModel

class LogoErrorChecker:
    def __init__(self, ocr_model_path, yolo_model_path):
        self.classifier = ImageClassifierONNX()
        self.ocr_model = OCRModel(ocr_model_path)
        self.people_searcher = PeopleSearcher()
        self.yolo_model = YoloModel(yolo_model_path)

    def check_errors(self, image_path):
        errors = []
        
        classification_result = self.classifier.predict(image_path)
        if classification_result < 0:
            errors.append("Ошибка отображения: логотип расположен неправильно или имеет деффект с размером")
        
        # OCR ------------------------------
        ocr_result = self.ocr_model.recognize(image_path)
        if 'error' in ocr_result:
            errors.append(f"OCR error: {ocr_result['error']}")
        
        # YOLO -----------------------------
        yolo_result = self.yolo_model.detect(image_path)
        if not yolo_result['detections']:
            errors.append("YOLO detection error: no objects detected.")
        
        return errors
from ml.classification_direction import ImageClassifierONNX
from ml.search_people import YOLOv8Inference

class LogoErrorChecker:
    def __init__(self, classification_model_path, yolo_people_model_path):
        self.classifier = ImageClassifierONNX(classification_model_path)
        self.people_detector = YOLOv8Inference(yolo_people_model_path)

    def check_errors(self, image_path):
        errors = []
        
        classification_result = self.classifier.predict(image_path)
        if classification_result < 0:
            errors.append("Ошибка отображения: логотип расположен неправильно или имеет деффект с размер")
        
        # YOLO для людей -------------------
        if not self.people_detector.detect_person(image_path):
            errors.append("Person detection error: no persons detected.")

        return errors
import tempfile
from app.ml.classification_direction import DirectionClassificator
from app.ml.ocr import OCR
from app.ml.search_people import SearchPeople
from app.ml.logo_detector import LogoDetector
from app.ml.classification_crop import CropClassificator
from PIL import Image

class LogoErrorChecker:
    def __init__(self,
            direction_path='app/ml/weights/classification_direction.onnx',
            people_path='app/ml/weights/search_people.pt',
            crop_path='app/ml/weights/classification_crop.onnx',
            logo_path='app/ml/weights/logo_detector.pt'
        ):

        self.direction_classificator = DirectionClassificator(direction_path)
        self.ocr_model = OCR()
        self.people_searcher = SearchPeople(people_path)
        self.crop_classificatior = CropClassificator(crop_path)
        self.logo_detector = LogoDetector(logo_path)

    def check_errors(self, image):
        errors = []
        
        # Сохраняем изображение во временный файл
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            image.save(tmp_file, format='PNG')
            tmp_file_path = tmp_file.name
        
        # Используем временный файл для предсказаний
        bboxes = self.logo_detector.predict(tmp_file_path)
        for bbox in bboxes:
            cropped_image = image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
            direction_info = self.direction_classificator.predict(cropped_image)
            if direction_info < 0:
                errors.append('Неправильное направление')

            logo_class = self.crop_classificatior.predict(cropped_image)
            # TODO: если класс является x, проверить цвет

        if self.people_searcher.detect(tmp_file_path):
            errors.append('Найден человек на фото')

        ocr_class = self.ocr_model.predict(tmp_file_path)
        # Вот с этим классом потом что-нибудь будем делать

        return errors

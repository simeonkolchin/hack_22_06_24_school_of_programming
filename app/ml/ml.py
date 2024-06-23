from ml.classification_direction import DirectionClassificator
from ml.ocr import OCR
from ml.search_people import SearchPeople
from ml.logo_detector import LogoDetector
from ml.classification_crop import CropClassificator
from easyocr import Reader
from PIL import Image, ImageDraw


class LogoErrorChecker:
    def __init__(self):
        self.direction_classificator = DirectionClassificator()
        self.ocr_model = OCR()
        self.people_searcher = SearchPeople()
        self.crop_classificatior = CropClassificator()
        self.logo_detector = LogoDetector()

    def check_errors(self, image_path):
        errors = []

        image = Image.open(image_path).convert('RGB')
    
        bboxes = self.logo_detector.predict(image_path)
        
        for bbox in bboxes:
            cropped_image = image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
            direction_info = self.direction_classificator.predict(cropped_image)
            
            if direction_info > 0:
                errors.append('Неправильное направление')

            logo_class = self.crop_classificator.predict(cropped_image)
            #TODO: если класс является x, проверить цвет
    

        if self.people_searcher.detect(image_path):
            errors.append('Найден человек на фото')
        
        ocr_class = self.ocr_model.predict(image_path)
        # Вот с этим классом потом что нибудь будем делать

        
        # classification_result = self.classifier.predict(image_path)
        # if classification_result < 0:
        #     errors.append("Ошибка отображения: логотип расположен неправильно или имеет деффект с размер")

        return errors


if __name__ == "__main__":
    checker = LogoErrorChecker()

    errors = checker.check_errors('/home/dmitrii/Desktop/hack_22_06_24_school_of_programming/data/original/demographics/Примеры некорректного брендирования/9 н.jpg')

    print(errors)

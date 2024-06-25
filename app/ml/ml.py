import tempfile
from app.ml.classification_direction import DirectionClassificator
from app.ml.classification_crop import CropClassificator
from app.ml.ocr import OCR
from app.ml.search_people import SearchPeople
from app.ml.logo_detector import LogoDetector
from app.ml.color_checker import ColorChecker

class LogoErrorChecker:
    def __init__(self,
            direction_path='app/ml/weights/classification_direction.onnx',
            people_path='app/ml/weights/search_people.pt',
            crop_path='app/ml/weights/classification_crop.onnx',
            logo_path='app/ml/weights/logo_detector.pt'
        ):

        """
        Инициализирует класс LogoErrorChecker с путями к весам моделей.
        
        :param direction_path: Путь к весам модели классификации направлений логотипов.
        :param people_path: Путь к весам модели поиска людей.
        :param crop_path: Путь к весам модели классификации обрезанных изображений.
        :param logo_path: Путь к весам модели детекции логотипов.
        """

        self.direction_classificator = DirectionClassificator(direction_path)
        self.ocr_model = OCR()
        self.people_searcher = SearchPeople(people_path)
        self.crop_classificatior = CropClassificator(crop_path)
        self.logo_detector = LogoDetector(logo_path)
        self.color_checker = ColorChecker()

    def check_errors(self, image):
        
        """
        Проверяет изображение на наличие ошибок, связанных с логотипами.
        
        :param image: Изображение, которое необходимо проверить.
        :return: Словарь с результатами проверки.
        
        Результат:
        - errors (list): Список общих ошибок, найденных на изображении.
        - ocr_class (str): Общий класс, определённый по всему изображению с помощью OCR.
        - bbox_results (list): Список результатов обработки для каждого найденного логотипа.
        
        bbox_results:
        - bbox (tuple): Координаты bounding box (bbox) логотипа.
        - cropped_class (str): Название класса, полученное при обработке обрезанного изображения нейросетью.
        - errors (list): Ошибки, связанные с текущим логотипом.
        - ocr_class (str): Класс логотипа, определённый по буквам на логотипе.
        - color_class (str): Класс логотипа, определённый по цвету.
        """

        result = {
            'errors': [],
            'ocr_class': None,
            'bbox_results': []
        }
        
        # Сохраняем изображение во временный файл
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            image.save(tmp_file, format='PNG')
            tmp_file_path = tmp_file.name
        
        # Используем временный файл для предсказаний
        bboxes = self.logo_detector.predict(tmp_file_path)
        for bbox in bboxes:
            bbox_result = {
                'bbox': bbox,
                'cropped_class': None,
                'errors': [],
                'ocr_class': None,
                'color_class': []
            }

            cropped_image = image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))

            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_small_file:
                image.save(tmp_small_file, format='PNG')
                tmp_small_file_path = tmp_small_file.name
            
            result['ocr_class'] = self.ocr_model.predict(tmp_small_file_path, threshold=0.34)

            bbox_result['cropped_class'] = self.crop_classificatior.predict(cropped_image)

            top_5_color_classes = self.color_checker.run(cropped_image)
            bbox_result['color_class'] = [str(k) + ' ' + str(v) + '%' for k, v in top_5_color_classes]

            if self.direction_classificator.predict(cropped_image) < 0 and bbox_result['cropped_class'] != 'dorogi':
                bbox_result['errors'].append('Неправильное направление или присутствуют другие искажения логотипа (искажение луча, неправильная форма логотипа и прочее)')

            #TODO: добавить проверку цвета

            result['bbox_results'].append(bbox_result)

        if self.people_searcher.detect(tmp_file_path):
            result['errors'].append('Найден человек на фото')

        result['ocr_class'] = self.ocr_model.predict(tmp_file_path)

        return result

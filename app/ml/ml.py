import tempfile
from app.ml.classification_direction import DirectionClassificator
from app.ml.classification_crop import CropClassificator
from app.ml.classification_check_good import CheckClassificator
from app.ml.ocr import OCR
from app.ml.search_people import SearchPeople
from app.ml.logo_detector import LogoDetector
from app.ml.color_checker import ColorChecker
from PIL import Image

import time


# Чет лень это в utils пихать, но код будет выглядеть более красиво так что решил сделать)
# (больше для себя, а то в ml.py много всего:) )
def save_image_to_temp_file(image: Image.Image) -> str:
    """
    Сохраняет изображение во временный файл и возвращает путь к этому файлу.
    
    :param image: Объект PIL.Image, представляющий изображение.
    :return: Строка с путем к временному файлу.
    """
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        image.save(tmp_file, format='PNG')
        tmp_file_path = tmp_file.name
    return tmp_file_path


class LogoErrorChecker:
    def __init__(self,
            direction_path='app/ml/weights/classification_direction.onnx',
            people_path='app/ml/weights/search_people.pt',
            crop_path='app/ml/weights/classification_crop.onnx',
            logo_path='app/ml/weights/logo_detector.pt',
            check_path='app/ml/weights/classification_check_good.onnx'
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
        self.crop_classificator = CropClassificator(crop_path)
        self.logo_detector = LogoDetector(logo_path)
        self.color_checker = ColorChecker(threshold=50)
        self.check_classificator = CheckClassificator(check_path)

    def check_errors(self, image):

        start = time.time()
        
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

        tmp_file_path = save_image_to_temp_file(image)

        result = {
            'bbox_results': [],
            'full_ocr_class': self.ocr_model.predict(tmp_file_path), # Если не None - надо вывести
            'people': self.people_searcher.detect(tmp_file_path) # Если не None - надо вывести
        }

        # Используем временный файл для предсказаний
        bboxes, norm_bboxes = self.logo_detector.predict(tmp_file_path)

        for bbox, norm_bboxes in zip(bboxes, norm_bboxes):
            cropped_image = image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
            tmp_small_file_path = save_image_to_temp_file(cropped_image)
    
            bbox_pred = {
                'cropped_class': self.crop_classificator.predict(cropped_image), # Что распознала нейронка
                'ocr_class': self.ocr_model.predict(tmp_small_file_path, threshold=0.34), # Что распознала OCR система
                'color_class': self.color_checker.run(cropped_image) # Возможные классы
            }

            bbox_info = {
                'bbox': bbox[:4], # координаты логотипа
                'errors': [], # строки об ошибках
                'info': [], # строки с инфой в целом, какой класс и тд
                'class': '-'
            }

            bbox_width = norm_bboxes[2] - norm_bboxes[0]
            bbox_height = norm_bboxes[3] - norm_bboxes[1]
            bbox_area = bbox_width * bbox_height

            if bbox_area < 0.01:
                bbox_info['errors'].append('Логотип занимает меньше 1% фотографии, скорее всего он находится слишком далеко / он слишком маленький')

            # Находим ошибки
            good_prob = self.check_classificator.predict(cropped_image)
            if good_prob < 0:
                bbox_info['errors'].append('Некорректный логотип (неизвестно почему)')

            if self.direction_classificator.predict(cropped_image) < 0 and bbox_pred['cropped_class'] != 'безопасные качественные дороги':
                bbox_info['errors'].append('Неправильное направление или присутствуют другие искажения логотипа (искажение луча, неправильная форма логотипа и прочее)')

            # Добавить проверку на шум, но это нужно тюнить модельку, возможно сделаю
            if bbox_pred['ocr_class'] is not None:
                ocr_class, ocr_dist = bbox_pred['ocr_class']
                if ocr_class in [x[0] for x in bbox_pred['color_class']]:
                    bbox_info['info'].append(f'Логотип класса: {ocr_class}')
                else:
                    cur_prob = 1 - 2.4 * ocr_dist
                    bbox_info['info'].append(f"На логотипе с вероятностью {round(cur_prob * 100, 2)} написано {ocr_class}, но цветовая гамма не совпадает")
                bbox_info['class'] = ocr_class
            else:
                bbox_info['info'].append(f'Не удалось прочитать что написано на логотипе')

                if bbox_pred['cropped_class'] is not None:
                    bbox_info['info'].append(f'Логотип очень похож на логотип класса {bbox_pred["cropped_class"]}')
                    bbox_info['class'] = bbox_pred['cropped_class']
                else:
                    bbox_info['info'].append(f'Не удалось классифицировать класс логотипа')

            if len(bbox_pred['color_class']):
                bbox_info['info'].append(f'Цветовая палитра совпадает с логотипами категорий: {", ".join([x[0] for x in bbox_pred["color_class"]])}')
                bbox_info['class'] = bbox_pred['color_class'][0][0]

            if len(bboxes) == 1 and result['full_ocr_class'] is not None and bbox_pred['ocr_class'] is None:
                full_ocr_class, full_ocr_dist = result['full_ocr_class']
                full_ocr_prob = 1 - 2.4 * full_ocr_dist
                bbox_info['info'].append(f"Рассмотрев все фото, с вероятностью {round(full_ocr_prob * 100)} на логотипе написано {full_ocr_class}")
                bbox_info['class'] = full_ocr_class

            result['bbox_results'].append(bbox_info)


        return result

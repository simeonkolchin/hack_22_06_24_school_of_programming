import easyocr
import cv2
import os
import re
import math
import Levenshtein

class OCR:
    """
    Класс для распознавания текста с изображений и классификации по определенным категориям.

    Атрибуты:
        reader (easyocr.Reader): Модель для распознавания текста.
        classes (list): Список категорий и ключевых слов для классификации.
    """
    def __init__(self, gpu=False):
        """
        Инициализирует OCR с использованием EasyOCR и заданным параметром GPU.

        Аргументы:
            gpu (bool): Флаг для использования GPU (по умолчанию False).
        """
        self.reader = easyocr.Reader(['ru'], gpu=gpu)
        self.classes = [
            ['образование'],
            ['демография'],
            ['цифровая', 'экономика'],
            ['наука', 'университеты'],
            ['культура'],
            ['магистральный план', 'энергетическая часть'],
            ['магистральный план', 'транспортная часть'],
            ['безопасные', 'качественные', 'дороги'],
            ['производительность', 'труда'],
            ['малое', 'среднее', 'предпринимательство'],
            ['здравоохранение'],
            ['экология'],
            ['жилье', 'городская', 'среда'],
            ['туризм', 'индустрия', 'гостеприимства'],
            ['международная', 'кооперация', 'экспорт']
        ]
    
    def recognize_text(self, image_path):
        """
        Распознает текст на изображении.

        Аргументы:
            image_path (str): Путь к изображению.

        Возвращает:
            str: Распознанный текст.
        """
        image = cv2.imread(image_path)
        results = self.reader.readtext(image, detail=0)
        recognized_text = ' '.join(x for x in results if len(x) >= 5)
        return recognized_text

    def get_dist(self, str1, str2):
        """
        Вычисляет нормализованное расстояние Левенштейна между двумя строками.

        Аргументы:
            str1 (str): Первая строка.
            str2 (str): Вторая строка.

        Возвращает:
            float: Нормализованное расстояние Левенштейна.
        """
        dist = Levenshtein.distance(str1, str2)
        return dist / len(str2)

    def classify_text(self, text):
        """
        Классифицирует текст по заданным категориям.

        Аргументы:
            text (str): Текст для классификации.

        Возвращает:
            tuple: Лучшая категория и соответствующее расстояние.
        """
        words = re.findall(r'\w+', text.lower())
        class_distances = {}

        for class_keywords in self.classes:
            distances = []
            best_words = []

            for keyword in class_keywords:
                cur_best = math.inf
                best_word = ''

                for word in words:
                    dist = self.get_dist(word, keyword)

                    if dist < cur_best:
                        cur_best = dist
                        best_word = word
                
                distances.append(cur_best)
                best_words.append(best_word)
            
            average_dist = sum(distances) / len(distances)
            class_name = ' '.join(class_keywords)
            class_distances[class_name] = average_dist

        #TODO ЕСЛИ ЕСТЬ РАВНЫЕ - ЗАПИСАТЬ ЧЕРЕЗ СЛЕШ
        #TODO есть пиркол что в urban_env есть "благоустройство общественной территории.. и тд тп, разные штуки"
        
        best_class = min(class_distances, key=class_distances.get)
        best_distance = class_distances[best_class]

        return best_class, best_distance

    def predict(self, image_path, threshold=0.25):
        """
        Выполняет предсказание категории для текста на изображении.

        Аргументы:
            image_path (str): Путь к изображению.
            threshold (float): Пороговое значение для уверенности в классификации (по умолчанию 0.25).

        Возвращает:
            str: Лучшая категория или сообщение о неудачной классификации.
        """
        recognized_text = self.recognize_text(image_path)
        best_class, best_distance = self.classify_text(recognized_text)

        if best_distance <= threshold:
            return [best_class, best_distance]
        else:
            return None

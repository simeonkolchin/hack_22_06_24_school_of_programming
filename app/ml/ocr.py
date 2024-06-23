import easyocr
import cv2
import os
import re
import math
import Levenshtein

class OCR:
    def __init__(self, gpu=False):
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
        image = cv2.imread(image_path)
        results = self.reader.readtext(image, detail=0)
        recognized_text = ' '.join(x for x in results if len(x) >= 5)
        return recognized_text

    def get_dist(self, str1, str2):
        dist = Levenshtein.distance(str1, str2)
        return dist / len(str2)

    def classify_text(self, text):
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
        
        best_class = min(class_distances, key=class_distances.get)
        best_distance = class_distances[best_class]

        return best_class, best_distance

    def predict(self, image_path, threshold=0.25):
        recognized_text = self.recognize_text(image_path)
        best_class, best_distance = self.classify_text(recognized_text)

        if best_distance <= threshold:
            return best_class
        else:
            return 'НЕ НАШЛА'


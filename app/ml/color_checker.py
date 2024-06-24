import cv2
import numpy as np
from PIL import Image
from collections import Counter

class ColorChecker:
    def __init__(self, threshold=40):
        self.threshold = threshold
        self.colors = {
            'демография': [[65, 145, 235], [75,165,200], [60, 125, 160]],
            'культура': [[120, 110, 170], [100, 110, 200], [80,75,120], [40,30,85]],
            'цифровая экономика': [[95, 135, 193], [110, 150, 205], [95,140,205]],
            'юезопасные дороги': [[210, 170, 85], [220, 200, 90]],
            'экоология': [[150, 200, 130], [100, 185, 140], [75, 110, 85], [145, 180, 125], [80, 120, 60]],
            'образование': [[125, 185, 220], [85, 190, 190], [75,115,175], [75,120,195], [110,155,180], [55,100,150]],
            'здравохранение': [[200,45,75], [85,45,50], [175,55,65], [160,110,140], [180,50,50], [140,60,85]],
            'международная кооперация и экспорт': [[45,55,70], [75,80,95]],
            'наука и университеты': [[60,135,185], [90,165,145], [80,165,120], [95,145,200], [80,140,205], [85,130,185]],
            'туризм': [[65,125,115], [85,170,155]],
            'городская среда': [[50,100,70], [55,120,80], [100,160,145], [100, 180, 130], [90,180,115], [90,175,125], [90,170,143], [70,90,50], [65,85,45]],
            'производительность труда': [[230,135,60], [220,140,65],[220,115,75]]
        }

    def run(self, pil_image):
        image = np.array(pil_image)
        height, width, _ = image.shape
        image_flat = image.reshape(-1, 3)
        counts = Counter()

        for color_name, color_values in self.colors.items():
            for color in color_values:
                color_array = np.array(color)
                diff = np.abs(image_flat - color_array)
                mask = np.sum(diff, axis=-1) <= self.threshold
                counts[color_name] += np.count_nonzero(mask)

        for key in counts.keys():
            counts[key] /= height * width
            counts[key] *= 100
            counts[key] = round(counts[key], 2)

        top_5 = sorted(counts.items(), key=lambda item: item[1], reverse=True)[:5]

        return top_5

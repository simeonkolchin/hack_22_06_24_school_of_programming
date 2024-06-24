import cv2
import numpy as np
from PIL import Image
from collections import Counter

class ColorChecker:
    def __init__(self, threshold=40):
        self.threshold = threshold
        self.colors = {
            'demographics': [[65, 145, 235], [75,165,200], [60, 125, 160]],
            'culture': [[120, 110, 170], [100, 110, 200]],
            'digital economics': [[95, 135, 193], [110, 150, 205], [95,140,205]],
            'dorogi': [[210, 170, 85], [220, 200, 90]],
            'ecology': [[150, 200, 130], [100, 185, 140], [75, 110, 85], [145, 180, 125], [80, 120, 60]],
            'education': [[125, 185, 220], [85, 190, 190], [75,115,175], [75,120,195], [110,155,180], [55,100,150]],
            'healthcare': [[200,45,75], [85,45,50], [175,55,65], [160,110,140], [180,50,50], [140,60,85]],
            'international-cooperation': [[45,55,70], [75,80,95]],
            'science-universities': [[60,135,185], [90,165,145], [80,165,120], [95,145,200], [80,140,205], [85,130,185]],
            'tourism': [[65,125,115], [85,170,155]],
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

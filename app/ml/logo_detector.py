import torch
from ultralytics import YOLO
import cv2
from torchvision.ops import box_iou
import torchvision

class LogoDetector:
    """
    Класс для обнаружения логотипов на изображениях с использованием модели YOLO.

    Атрибуты:
        model (YOLO): Загруженная модель YOLO для обнаружения логотипов.
    """

    def __init__(self, model_path='app/ml/weights/logo_detector.pt'):
        """
        Инициализирует LogoDetector с заданным путем к модели.

        Аргументы:
            model_path (str): Путь к модели YOLO.
        """
        self.model = YOLO(model_path)

    def non_max_suppression(self, bboxes, threshold=0.5):
        """
        Применяет non-max suppression (NMS) для удаления перекрывающихся прямоугольников.

        Аргументы:
            bboxes (list): Список прямоугольников (bbox) в формате [x1, y1, x2, y2, score].
            threshold (float): Пороговое значение для NMS (по умолчанию 0.5).

        Возвращает:
            list: Список прямоугольников после применения NMS.
        """

        if len(bboxes) == 0:
            return []
    
        boxes = torch.tensor([bbox[:4] for bbox in bboxes], dtype=torch.float32)
        scores = torch.tensor([bbox[4] for bbox in bboxes], dtype=torch.float32)

        selected_indices = torchvision.ops.nms(boxes, scores, threshold)
        
        selected_bboxes = [bboxes[i] for i in selected_indices]
        return selected_bboxes

    def predict(self, image_path, conf_threshold=0.25, iou_threshold=0.1):
        """
        Выполняет предсказание логотипов на изображении.

        Аргументы:
            image_path (str): Путь к изображению.
            conf_threshold (float): Пороговое значение для уверенности модели (по умолчанию 0.25).
            iou_threshold (float): Пороговое значение для NMS (по умолчанию 0.1).

        Возвращает:
            list: Список прямоугольников с координатами и вероятностями в формате (x1, y1, x2, y2, score).
        """

        image = cv2.imread(image_path)
        results = self.model(image, verbose=False, conf=conf_threshold)
        
        bboxes = []
        for x1, y1, x2, y2, prob, _ in results[0].boxes.data.cpu().numpy():
            bboxes.append([x1, y1, x2, y2, prob])
        
        selected_bboxes = self.non_max_suppression(bboxes, iou_threshold)
        xyxy_bboxes = [(int(x1), int(y1), int(x2), int(y2), float(prob)) for x1, y1, x2, y2, prob in selected_bboxes]

        return xyxy_bboxes

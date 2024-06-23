import torch
from ultralytics import YOLO
import cv2
import numpy as np
from torchvision.ops import box_iou
import torchvision

class LogoDetector:
    def __init__(self, model_path='app/ml/weights/logo_detector.pt'):
        self.model = YOLO(model_path)

    def non_max_suppression(self, bboxes, threshold=0.5):
        if len(bboxes) == 0:
            return []
    
        boxes = torch.tensor([bbox[:4] for bbox in bboxes], dtype=torch.float32)
        scores = torch.tensor([bbox[4] for bbox in bboxes], dtype=torch.float32)

        selected_indices = torchvision.ops.nms(boxes, scores, threshold)
        
        selected_bboxes = [bboxes[i] for i in selected_indices]
        return selected_bboxes

    def predict(self, image_path, conf_threshold=0.25, iou_threshold=0.1):
        image = cv2.imread(image_path)
        results = self.model(image, verbose=False, conf=conf_threshold)
        
        bboxes = []
        for x1, y1, x2, y2, prob, _ in results[0].boxes.data.cpu().numpy():
            bboxes.append([x1, y1, x2, y2, prob])
        
        selected_bboxes = self.non_max_suppression(bboxes, iou_threshold)
        xyxy_bboxes = [(int(x1), int(y1), int(x2), int(y2), float(prob)) for x1, y1, x2, y2, prob in selected_bboxes]

        return xyxy_bboxes

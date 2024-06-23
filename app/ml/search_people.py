from ultralytics import YOLO

class SearchPeople:
    def __init__(self, model_path='yolov8s.pt'):
        self.model = YOLO(model_path)
    
    def detect(self, image_path):
        results = self.model(image_path, conf=0.3)
        if 0 in results[0].boxes.data[:, 5]:
            return True
        else:
            return False

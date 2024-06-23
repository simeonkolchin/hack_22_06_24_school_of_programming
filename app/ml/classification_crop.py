import onnxruntime as ort
import torchvision.transforms as transforms
from PIL import Image
import numpy as np

class CropClassificator:
    def __init__(self, model_path='app/ml/weights/classification_crop.onnx'):
        self.model = ort.InferenceSession(model_path)

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
        ])

        self.class_names = [
            'culture',
            'demographics',
            'dorogi',
            'ecology',
            'education',
            'healthcare',
            'urban_env'
        ]
    
    def predict(self, image):
        image = self.transform(image).unsqueeze(0).numpy()

        inputs = {self.model.get_inputs()[0].name: image}
        outputs = self.model.run(None, inputs)
        outputs = outputs[0]

        if np.max(outputs) < 5:
            return 'None'

        predicted = np.argmax(outputs, axis=1)
        predicted_class = self.class_names[predicted.item()]

        return predicted_class
    

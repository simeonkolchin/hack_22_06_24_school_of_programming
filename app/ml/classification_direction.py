import onnxruntime as ort
import torchvision.transforms as transforms
from PIL import Image
import numpy as np

class ImageClassifierONNX:
    def __init__(self, classification_model_path):
        self.onnx_session = ort.InferenceSession(classification_model_path)
        self.input_name = self.onnx_session.get_inputs()[0].name
        self.output_name = self.onnx_session.get_outputs()[0].name
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def predict(self, image_path):
        image = Image.open(image_path).convert('RGB')
        image = self.transform(image).unsqueeze(0).numpy()
        outputs = self.onnx_session.run([self.output_name], {self.input_name: image})
        output = outputs[0][0][0]
        return output
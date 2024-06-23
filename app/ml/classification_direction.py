import onnxruntime as ort
import torchvision.transforms as transforms
from PIL import Image
import numpy as np

class DirectionClassificator:
    def __init__(self, classification_model_path='weights/classification_direction.onnx'):

        import os
        print(os.path.exists(classification_model_path))

        self.onnx_session = ort.InferenceSession(classification_model_path)
        self.input_name = self.onnx_session.get_inputs()[0].name
        self.output_name = self.onnx_session.get_outputs()[0].name
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def predict(self, image):
        image = self.transform(image).unsqueeze(0).numpy()
        outputs = self.onnx_session.run([self.output_name], {self.input_name: image})
        output = outputs[0][0][0]
        return output


if __name__ == "__main__":
    classifier = DirectionClassificator(classification_model_path='weights/classification_direction.onnx')

    image_path = '/home/dmitrii/Desktop/hack_22_06_24_school_of_programming/data/classification_crop/ecology/ekologia15.jpg'
    image = Image.open(image_path).convert('RGB')
    
    prediction = classifier.predict(image)

    print(f'Predicted class: {prediction}')

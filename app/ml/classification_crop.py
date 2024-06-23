import onnxruntime as ort
import torchvision.transforms as transforms
from PIL import Image
import numpy as np

class CropClassificatorONNX:
    def __init__(self, model_path='weights/classification_crop.onnx'):
        self.model = ort.InferenceSession(model_path)

        self.transform = transforms.Compose([
            transforms.Resize(224),
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
    

if __name__ == "__main__":
    classifier = CropClassificatorONNX(model_path='classification_crop.onnx')

    image = Image.open('/home/dmitrii/Desktop/hack_22_06_24_school_of_programming/data/classification_crop/ecology/ekologia1.jpg').convert('RGB')
    prediction = classifier.predict(image)

    print(f'Predicted class: {prediction}')

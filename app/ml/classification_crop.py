import torch
import torchvision.transforms as transforms
from PIL import Image
import torchvision.models as models
import torch.nn as nn

class CropClassificator:
    def __init__(self, model_path='weights/classification_crop.pth'):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
        self.model = models.mobilenet_v3_large(pretrained=False)
        self.model.classifier[3] = nn.Linear(self.model.classifier[3].in_features, 7)
        
        if model_path:
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        
        self.model.to(self.device)
        self.model.eval()

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
        image = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(image)

        if torch.max(outputs) < 5:
            return 'None'

        _, predicted = torch.max(outputs, 1)
        predicted_class = self.class_names[predicted.item()]

        return predicted_class
    

if __name__ == "__main__":
    classifier = CropClassificator(model_path='model.pth')

    image = Image.open('/home/dmitrii/Desktop/hack_22_06_24_school_of_programming/data/classification_crop/ecology/ekologia1.jpg').convert('RGB')
    prediction = classifier.predict(image)

    print(f'Predicted class: {prediction}')

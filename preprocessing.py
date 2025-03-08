import os
from torch.utils.data import Dataset
from torchvision import transforms
from PIL import Image
class CustomDataset(Dataset):
    def __init__(self, folders, transform=None):
        self.folders = folders
        self.file_image = []
        self.label = []
        self.transform = transforms.Compose(
            [
                transforms.Resize((224,224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])         
            ]
        )
        self.class_to_idx = None
        self.idx_to_class = None
    
    # def mix_data(self, folders):
        for folder in sorted(os.listdir(self.folders)):
            file_path = os.path.join(self.folders, folder)
            image_path = os.listdir(file_path)
            for img in image_path:
                img_pic = os.path.join(file_path, img)
                self.file_image.append(img_pic)
                self.label.append(folder)
    def __len__(self):
        return len(self.file_image)
    def convert(self):
        self.class_to_idx = {label : idx for idx, label in sorted(set(self.label))}
        self.idx_to_class = {idx : label for label,idx in self.class_to_idx}
    def __getitem__(self,idx):
        image = Image.open(self.file_image[idx]).convert("RGB")
        label = self.class_to_idx[self.label[idx]]
        if self.transform:
            image = self.transform(image)
        return image, label        
    
            
        
        
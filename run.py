from preprocessing import CustomDataset
from resnet50 import Mymodel
from torch.utils.data import DataLoader, random_split
import torch
# from preprocessing import CustomDataset
# from resnet50 import Mymodel
from torch.utils.data import DataLoader, random_split
import torch.optim as optim
# import torch
def split(dataset):
    train_ratio = 0.8
    train_size = int(train_ratio * len(dataset))
    valid_size = len(dataset) - train_size

    # Split dataset
    train_dataset, valid_dataset = random_split(dataset, [train_size, valid_size])

    # Create DataLoaders
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    valid_loader = DataLoader(valid_dataset, batch_size=32, shuffle=False)
    return train_loader, valid_loader

def train_model(model, train_loader, valid_loader, epochs=20, lr=0.001, patience=5):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    best_loss = float('inf')
    counter = 0  # Tracks epochs without improvement

    for epoch in range(epochs):
        # Training
        model.train()
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
        
        # Validation
        model.eval()
        valid_loss = 0.0
        with torch.no_grad():
            for images, labels in valid_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                valid_loss += loss.item()
        
        valid_loss /= len(valid_loader)
        print(f"Epoch {epoch+1}/{epochs}, Validation Loss: {valid_loss:.4f}")

        # Early Stopping
        if valid_loss < best_loss:
            best_loss = valid_loss
            counter = 0  # Reset counter if validation loss improves
            torch.save(model.state_dict(), "best_model.pth")  # Save best model
        else:
            counter += 1
            print(f"No improvement for {counter} epochs")
            if counter >= patience:
                print("Early stopping triggered!")
                break  # Stop training
            

dir = 'dir-dtaa'           
model = Mymodel()
dataset = CustomDataset(dir)
train_loader, valid_loader = split(dataset)
train_model(model, train_loader, valid_loader, 10, 0.05,5)
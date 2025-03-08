from torchvision import models
# import torch
import torch.nn as nn


class Mymodel(nn.Module):
    def __init__(self, model =None):
        super(Mymodel,self).__init__()
        self.model = models.resnet50(pretrained = True)
    def forward(self,x):
        return self.model(x)

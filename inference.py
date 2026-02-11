"""
Inference module — placeholder for your model prediction logic.

Replace the `predict` function with your actual model inference code.
The function signature and return format should be kept consistent
so the UI renders correctly.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from streamlit.runtime.uploaded_file_manager import UploadedFile

import cv2 
import numpy as np
import torch
import torch.nn as nn
import cv2
import numpy as np
from torchvision.models import  vgg16, VGG16_Weights
from PIL import Image
from torch.nn import functional as F
from io import BytesIO
IMAGENET_MEAN = torch.tensor([0.485, 0.456, 0.406]).view(3,1,1)
IMAGENET_STD  = torch.tensor([0.229, 0.224, 0.225]).view(3,1,1)
device = torch.device("cpu")

def fft_highpass_preprocess(img_rgb, r=8, eps=1e-8):
    """
    img_rgb: np.ndarray (224,224,3), uint8 atau float [0,255]
    return: np.ndarray (224,224,3) float32, normalized [0,1]
    """


    # 2) grayscale
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)

    # 3) FFT2 + shift
    X = np.fft.fft2(gray)
    Xs = np.fft.fftshift(X)

    # 4) ideal high-pass mask (radius r)
    h, w = gray.shape
    cy, cx = h // 2, w // 2
    Y, Xc = np.ogrid[:h, :w]
    dist2 = (Y - cy)**2 + (Xc - cx)**2
    mask = (dist2 >= r*r).astype(np.float32)

    Xhp_s = Xs * mask

    # 5) inverse shift + IFFT
    Xhp = np.fft.ifftshift(Xhp_s)
    xhp = np.fft.ifft2(Xhp)

    # 6) magnitude + log
    mag = np.abs(xhp)
    hplog = np.log1p(mag)

    # 7) normalize [0,1]
    mmin, mmax = hplog.min(), hplog.max()
    hpgray = (hplog - mmin) / (mmax - mmin + eps)

    # 8) replicate ke 3 channel
    x_fft = np.repeat(hpgray[..., None], 3, axis=2).astype(np.float32)

    return x_fft


class BiCrossAttentionFusion(nn.Module):
    def __init__(self, C=256, nheads=16, attn_dropout=0.0):
        super().__init__()
        self.C = C
        self.nheads = nheads

        self.attn_rgb_from_fft = nn.MultiheadAttention(
            embed_dim=C,num_heads=nheads, dropout=attn_dropout, batch_first=False
        )
        
        self.attn_fft_from_rgb = nn.MultiheadAttention(
            embed_dim=C,num_heads=nheads, dropout=attn_dropout, batch_first=False
        )
    def forward(self, F_rgb, F_fft):
        rgb = F_rgb.flatten(2).permute(2, 0, 1)  # (H*W, B, C)
        fft = F_fft.flatten(2).permute(2, 0, 1)  # (H*W, B, C)
        z_rgb, _ = self.attn_rgb_from_fft(query=rgb, key=fft, value=fft)
        z_fft, _ = self.attn_fft_from_rgb(query=fft, key=rgb, value=rgb)
        z_rgb = z_rgb + rgb
        z_fft = z_fft + fft
        z_rgb = z_rgb.permute(1, 2, 0).contiguous()
        z_fft = z_fft.permute(1, 2, 0).contiguous()
        Z_tokens = torch.cat([z_rgb, z_fft], dim=1) 
        Z= Z_tokens.mean(dim=2)
        return  Z      


class ClassifierHead(nn.Module):
    def __init__(self, in_dim=512, num_classes=2, use_bn=True, p=0.2):
        super().__init__()
        def block(a, b):
            layers = [nn.Linear(a, b)]
            if use_bn:
                layers.append(nn.BatchNorm1d(b))
            layers.append(nn.ReLU(inplace=True))
            if p > 0:
                layers.append(nn.Dropout(p))
            return nn.Sequential(*layers)

        self.fc1 = block(in_dim, 256)
        self.fc2 = block(256, 128)
        self.fc3 = nn.Linear(128, num_classes) 

    def forward(self, z):
        z = self.fc1(z)   
        z = self.fc2(z)   
        logits = self.fc3(z)  
        return logits

def make_vgg17():
    weights = VGG16_Weights.IMAGENET1K_V1
    vgg = vgg16(weights=weights)
    return vgg.features[:17]

class FullModel(nn.Module):
    def __init__(self, vgg_rgb, vgg_fft, fusion, head):
        super().__init__()
        self.vgg_rgb = vgg_rgb          # output (B,256,28,28)
        self.vgg_fft = vgg_fft          # output (B,256,28,28)
        self.fusion = fusion            # output Z (B,512)
        self.head = head                # output logits (B,2)

    def forward(self, x_rgb, x_fft):
        f_rgb = self.vgg_rgb(x_rgb)     # (B,256,28,28)
        f_fft = self.vgg_fft(x_fft)     # (B,256,28,28)
        Z = self.fusion(f_rgb, f_fft)   # (B,512)
        logits = self.head(Z)           # (B,2)
        return logits
    
mymodel = FullModel(
    vgg_rgb=make_vgg17(),
    vgg_fft=make_vgg17(),
    fusion=BiCrossAttentionFusion(C=256, nheads=16, attn_dropout=0.0),
    head=ClassifierHead(in_dim=512, num_classes=2, use_bn=True, p=0.2)
)
mymodel.load_state_dict(torch.load("models/best_model.pth", map_location=device)["model_state_dict"])
mymodel.eval()
def predict(uploaded_file: UploadedFile) -> dict:
    """
    Run spoof/real prediction on a single uploaded image.

    Args:
        uploaded_file: A Streamlit UploadedFile object (image).

    Returns:
        dict with the following keys:
            - "label"      : str   → "real" or "spoof"
            - "confidence" : float → confidence score between 0.0 and 1.0
            - "details"    : dict  → (optional) any extra info you want to display

    Example return:
        {
            "label": "real",
            "confidence": 0.97,
            "details": {"model": "resnet50", "latency_ms": 42}
        }
    """

    # ┌──────────────────────────────────────────────────────────┐
    # │  TODO: Replace this dummy logic with your real model     │
    # │  inference code. You have access to:                     │
    # │    - uploaded_file.getvalue()  → raw bytes               │
    # │    - uploaded_file.name        → original filename        │
    # │    - You can use PIL, torch, tf, onnx, etc.              │
    # └──────────────────────────────────────────────────────────┘
    img = Image.open(BytesIO(uploaded_file.getvalue()))
    img = img.resize((224, 224))

    img_np = np.array(img).astype("float32") / 255.0
    img_np = np.transpose(img_np, (2, 0, 1))
    img_tensor = torch.from_numpy(img_np)
    img_tensor = (img_tensor - IMAGENET_MEAN) / IMAGENET_STD
    img_tensor = img_tensor.unsqueeze(0).to(device)

    fft_img = fft_highpass_preprocess(np.array(img))
    fft_img = np.transpose(fft_img.astype("float32"), (2, 0, 1))
    fft_tensor = torch.from_numpy(fft_img)
    fft_tensor = (fft_tensor - IMAGENET_MEAN) / IMAGENET_STD
    fft_tensor = fft_tensor.unsqueeze(0).to(device)

    with torch.no_grad():
        output = mymodel(img_tensor, fft_tensor)
        _, predicted = torch.max(output, 1)
        probs = F.softmax(output, dim=1)
        confidence, label = torch.max(probs, 1)
    label = "real" if label.item() == 0 else "spoof"

    return {
        "label": label,
        "confidence": confidence,
        "details": {},
    }

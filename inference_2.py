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
from PIL import Image
import torchvision
import random
from dataclasses import dataclass

import cv2
import numpy as np
import torch
import torch.nn as nn
import torchvision
from PIL import Image
from torchvision import transforms
from torchvision.transforms import functional as TF
from typing import List, Dict

@dataclass
class TrainConfig:
    data_root: str = "./data_root"
    batch_size: int = 16
    num_workers: int = 4
    epochs: int = 10
    lr_head: float = 1e-4
    lr_backbone: float = 1e-4
    weight_decay: float = 1e-4
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    freeze_backbone_epochs: int = 2
# 3) Paired random crop/flip transform (same geometry for RGB & FFT pipeline)
@dataclass
class AugConfig:
    patch_size: int = 224
    scale_min: float = 0.6
    scale_max: float = 1.0
    ratio_min: float = 3/4
    ratio_max: float = 4/3
    hflip_p: float = 0.5
    rot_deg: float = 3.0  # small rotation


# 1) Color conversion: RGB -> Grayscale (torch)
def rgb_to_gray_torch(x: torch.Tensor) -> torch.Tensor:
    """
    x: torch.Tensor, shape [3, H, W], float in [0, 1]
    returns: [H, W] grayscale tensor
    """
    assert x.ndim == 3 and x.shape[0] == 3
    r, g, b = x[0], x[1], x[2]
    # Standard RGB to grayscale conversion
    gray = 0.299 * r + 0.587 * g + 0.114 * b
    return gray

# 2) FFT feature extractor (High-pass filter + FFT + Normalize)
@dataclass
class FFTConfig:
    patch_size: int = 224
    highpass_radius: int = 8          # remove low-freq center circle
    eps: float = 1e-8
    per_patch_standardize: bool = False

class FFTFeatureExtractor(nn.Module):
    """
    Input: RGB patch tensor [3,H,W] float [0,1]
    Output: FFT feature [1,H,W] float (1 channel grayscale FFT)
    Exactly matches research.ipynb fft_highpass_preprocess()
    """
    def __init__(self, cfg: FFTConfig):
        super().__init__()
        self.cfg = cfg

    def _highpass_mask(self, h: int, w: int, radius: int, device) -> torch.Tensor:
        """Create ideal high-pass mask (remove center circle with radius r)"""
        yy, xx = torch.meshgrid(
            torch.arange(h, device=device),
            torch.arange(w, device=device),
            indexing="ij"
        )
        cy, cx = h // 2, w // 2
        dist_squared = (yy - cy).float() ** 2 + (xx - cx).float() ** 2
        mask = (dist_squared >= radius * radius).float()
        return mask  # [H,W]

    def forward(self, rgb_patch: torch.Tensor) -> torch.Tensor:
        """
        rgb_patch: [3,H,W], float [0,1]
        returns: [1,H,W] FFT features (1 channel grayscale)

        Follows exact flow from research.ipynb:
        1. Grayscale
        2. FFT2
        3. FFTshift
        4. High-pass mask
        5. Inverse FFTshift
        6. IFFT2
        7. Magnitude + log
        8. Normalize [0,1]
        9. Output 1 channel
        """
        assert rgb_patch.ndim == 3 and rgb_patch.shape[0] == 3
        _, h, w = rgb_patch.shape
        assert h == self.cfg.patch_size and w == self.cfg.patch_size, "Patch size mismatch"

        # Step 1: Convert to grayscale
        gray = rgb_to_gray_torch(rgb_patch)  # [H,W] in [0,1]

        # Scale to [0,255] to match NumPy cv2.cvtColor output
        gray = gray * 255.0  # [H,W] in [0,255]

        # Step 2: FFT2
        X = torch.fft.fft2(gray)

        # Step 3: FFTshift (move zero frequency to center)
        Xs = torch.fft.fftshift(X)

        # Step 4: Apply ideal high-pass mask
        hp_mask = self._highpass_mask(h, w, self.cfg.highpass_radius, Xs.device)
        Xhp_s = Xs * hp_mask

        # Step 5: Inverse FFTshift
        Xhp = torch.fft.ifftshift(Xhp_s)

        # Step 6: IFFT2 (back to spatial domain)
        xhp = torch.fft.ifft2(Xhp)

        # Step 7: Magnitude + log
        mag = torch.abs(xhp)
        hplog = torch.log1p(mag)

        # Step 8: Normalize to [0,1]
        mmin = hplog.min()
        mmax = hplog.max()
        hpgray = (hplog - mmin) / (mmax - mmin + self.cfg.eps)

        # Step 9: Output as 1 channel [1,H,W]
        feat = hpgray.unsqueeze(0)  # [1,H,W]

        return feat

class PairedAugment:
    """
    Applies the same random geometric transforms to a PIL image,
    then outputs a tensor patch in [0,1].
    (FFT computed later from this tensor patch.)
    """
    def __init__(self, cfg: AugConfig):
        self.cfg = cfg

    def __call__(self, img: Image.Image) -> torch.Tensor:
        # RandomResizedCrop params
        i, j, h, w = transforms.RandomResizedCrop.get_params(
            img,
            scale=(self.cfg.scale_min, self.cfg.scale_max),
            ratio=(self.cfg.ratio_min, self.cfg.ratio_max)
        )
        img = TF.resized_crop(img, i, j, h, w, size=[self.cfg.patch_size, self.cfg.patch_size])

        # Random small rotation
        angle = random.uniform(-self.cfg.rot_deg, self.cfg.rot_deg)
        img = TF.rotate(img, angle=angle, interpolation=transforms.InterpolationMode.BILINEAR, fill=0)

        # Random horizontal flip
        if random.random() < self.cfg.hflip_p:
            img = TF.hflip(img)

        # To tensor [0,1]
        x = TF.to_tensor(img)  # [3,H,W]
        return x

class VGG16Backbone(nn.Module):
    def __init__(self, pretrained: bool = True, in_channels: int = 3):
        super().__init__()
        weights = torchvision.models.VGG16_Weights.IMAGENET1K_V1 if pretrained else None
        vgg = torchvision.models.vgg16(weights=weights)

        # If input is 1 channel, modify first conv layer
        if in_channels != 3:
            # Get original first conv layer
            original_conv = vgg.features[0]
            # Create new conv layer with 1 input channel
            new_conv = nn.Conv2d(
                in_channels,
                original_conv.out_channels,
                kernel_size=original_conv.kernel_size,
                stride=original_conv.stride,
                padding=original_conv.padding
            )
            # Initialize: average the pretrained weights across RGB channels
            if pretrained:
                with torch.no_grad():
                    new_conv.weight[:, :, :, :] = original_conv.weight.mean(dim=1, keepdim=True)
                    new_conv.bias = original_conv.bias

            # Replace first conv layer
            vgg.features[0] = new_conv

        self.features = vgg.features  # outputs Bx512x7x7 for 224 input

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.features(x)  # [B,512,7,7]

class CrossAttentionBlock(nn.Module):
    """
    Transformer-style cross-attention block:
    - Q from tokens_a
    - K,V from tokens_b
    """
    def __init__(self, dim: int = 512, num_heads: int = 8, dropout: float = 0.1, ffn_mult: int = 4):
        super().__init__()
        self.mha = nn.MultiheadAttention(embed_dim=dim, num_heads=num_heads, dropout=dropout, batch_first=True)
        self.norm1 = nn.LayerNorm(dim)

        self.ffn = nn.Sequential(
            nn.Linear(dim, dim * ffn_mult),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(dim * ffn_mult, dim),
            nn.Dropout(dropout),
        )
        self.norm2 = nn.LayerNorm(dim)

    def forward(self, tokens_a: torch.Tensor, tokens_b: torch.Tensor) -> torch.Tensor:
        """
        tokens_a: [B, N, D]
        tokens_b: [B, M, D]
        """
        attn_out, _ = self.mha(tokens_a, tokens_b, tokens_b, need_weights=False)
        x = self.norm1(tokens_a + attn_out)
        ffn_out = self.ffn(x)
        x = self.norm2(x + ffn_out)
        return x

class TwoStreamVGG16_CrossAttn(nn.Module):
    def __init__(
        self,
        pretrained_backbones: bool = True,
        attn_heads: int = 8,
        attn_dropout: float = 0.1,
        bidirectional: bool = True,   # RGB<-FFT and FFT<-RGB
    ):
        super().__init__()
        self.rgb_backbone = VGG16Backbone(pretrained=pretrained_backbones, in_channels=3)
        self.fft_backbone = VGG16Backbone(pretrained=pretrained_backbones, in_channels=1)  # FFT is 1-channel grayscale

        self.bidirectional = bidirectional
        self.cross_rgb_from_fft = CrossAttentionBlock(dim=512, num_heads=attn_heads, dropout=attn_dropout)
        if self.bidirectional:
            self.cross_fft_from_rgb = CrossAttentionBlock(dim=512, num_heads=attn_heads, dropout=attn_dropout)

        self.head = nn.Sequential(
            nn.Linear(1024 if self.bidirectional else 512, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(256, 1)  # logit
        )

    @staticmethod
    def _to_tokens(feat: torch.Tensor) -> torch.Tensor:
        # feat: [B,512,7,7] -> [B,49,512]
        b, c, h, w = feat.shape
        tokens = feat.view(b, c, h * w).transpose(1, 2).contiguous()
        return tokens

    def forward(self, x_rgb: torch.Tensor, x_fft: torch.Tensor) -> torch.Tensor:
        f_rgb = self.rgb_backbone(x_rgb)  # [B,512,7,7]
        f_fft = self.fft_backbone(x_fft)  # [B,512,7,7]

        t_rgb = self._to_tokens(f_rgb)    # [B,49,512]
        t_fft = self._to_tokens(f_fft)    # [B,49,512]

        t_rgb_att = self.cross_rgb_from_fft(t_rgb, t_fft)
        v_rgb = t_rgb_att.mean(dim=1)     # [B,512]

        if self.bidirectional:
            t_fft_att = self.cross_fft_from_rgb(t_fft, t_rgb)
            v_fft = t_fft_att.mean(dim=1) # [B,512]
            v = torch.cat([v_rgb, v_fft], dim=1)  # [B,1024]
        else:
            v = v_rgb  # [B,512]

        logit = self.head(v).squeeze(1)   # [B]
        return logit

def _make_patches(img_rgb: np.ndarray, patch_size: int, k: int = 16) -> List[torch.Tensor]:
    """
    Create K patches using random resized crops (inference-time augmentation).
    img_rgb: numpy array [H,W,3] uint8
    Returns list of RGB tensors [3,patch,patch] in [0,1]
    """
    import cv2
    from PIL import Image
    patches = []
    img_pil = Image.fromarray(img_rgb)
    for _ in range(k):
        i, j, h, w = transforms.RandomResizedCrop.get_params(img_pil, scale=(0.6, 1.0), ratio=(3/4, 4/3))
        patch = TF.resized_crop(img_pil, i, j, h, w, size=[patch_size, patch_size])
        patches.append(TF.to_tensor(patch))
    return patches

fft_extractor = FFTFeatureExtractor(FFTConfig())
model = TwoStreamVGG16_CrossAttn(
    pretrained_backbones=True,
    attn_heads=8,
    attn_dropout=0.1,
    bidirectional=True
).to("cpu")
ckpt = torch.load("models/model_vers-2.pt", map_location="cpu")
print("model_vers-2.pt")
model.load_state_dict(ckpt["model_state"])
threshold = ckpt["val_threshold"]

def predict(
    model = model,
    fft_extractor: FFTFeatureExtractor= fft_extractor,
    device: str = "cpu",
    k_patches: int = 16,
    threshold: float = threshold,
    uploaded_file: UploadedFile = None
):
    model.eval()

    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise FileNotFoundError(f"Cannot read image: {uploaded_file}")
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    patches = _make_patches(img_rgb, patch_size=fft_extractor.cfg.patch_size, k=k_patches)

    logits = []
    for rgb_patch in patches:
        # rgb_patch is [3,H,W] in [0,1]
        fft_patch = fft_extractor(rgb_patch)  # [1,H,W] EXACT match dataset

        rgb_norm = TF.normalize(
            rgb_patch,
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )

        x_rgb = rgb_norm.unsqueeze(0).to(device)
        x_fft = fft_patch.unsqueeze(0).to(device)

        logit = model(x_rgb, x_fft).view(-1).item()
        logits.append(logit)

    avg_logit = float(np.mean(logits))
    prob_spoof = float(torch.sigmoid(torch.tensor(avg_logit)).item())
    pred = "spoof" if prob_spoof >= threshold else "real"
    confidence = max(prob_spoof, 1.0 - prob_spoof)
    return {
        "confidence": confidence,
        "label": pred,
        "details": {
            "logits": logits,
            "avg_logit": avg_logit,
            "threshold": threshold
        }
    }



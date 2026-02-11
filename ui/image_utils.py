"""
Image utility functions for encoding and processing uploaded files.
"""

from __future__ import annotations

import base64
from io import BytesIO
from typing import TYPE_CHECKING

from PIL import Image

if TYPE_CHECKING:
    from streamlit.runtime.uploaded_file_manager import UploadedFile


# Supported MIME types
ALLOWED_TYPES = ["png", "jpg", "jpeg", "webp"]


def file_to_base64(uploaded_file: UploadedFile) -> str:
    """Convert a Streamlit UploadedFile to a base64-encoded string."""
    data = uploaded_file.getvalue()
    return base64.b64encode(data).decode("utf-8")


def get_mime_type(uploaded_file: UploadedFile) -> str:
    """Return the MIME type string for an uploaded file."""
    name = uploaded_file.name.lower()
    if name.endswith(".png"):
        return "image/png"
    if name.endswith((".jpg", ".jpeg")):
        return "image/jpeg"
    if name.endswith(".webp"):
        return "image/webp"
    return "image/png"


def open_image(uploaded_file: UploadedFile) -> Image.Image:
    """Open a Streamlit uploaded file as a PIL Image."""
    return Image.open(BytesIO(uploaded_file.getvalue())).convert("RGB")


def get_image_dimensions(uploaded_file: UploadedFile) -> tuple[int, int]:
    """Return (width, height) of the uploaded image."""
    img = open_image(uploaded_file)
    return img.size


def format_file_size(size_bytes: int) -> str:
    """Format byte count to human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"

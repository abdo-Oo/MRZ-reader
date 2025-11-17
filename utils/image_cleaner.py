import numpy as np
from PIL import Image

def normalize_image(input_img):
    """
    Ensures the image is valid for PassportEye:
    - Convert to PIL.Image
    - Convert to RGB
    - Return clean NumPy array (H, W, 3)
    """
    # If already numpy → convert to PIL
    if isinstance(input_img, np.ndarray):
        img = Image.fromarray(input_img)
    else:
        img = input_img

    # Convert to RGB (removes alpha / grayscale)
    img = img.convert("RGB")

    # Return RGB NumPy array
    return np.asarray(img).copy()

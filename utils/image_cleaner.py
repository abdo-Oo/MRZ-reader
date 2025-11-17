import numpy as np
from PIL import Image

def normalize_image(input_img):
    if isinstance(input_img, np.ndarray):
        img = Image.fromarray(input_img)
    else:
        img = input_img

    img = img.convert("RGB")
    return np.array(img).astype("uint8")

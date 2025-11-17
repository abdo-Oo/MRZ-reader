import cv2
import numpy as np
from passporteye import read_mrz
from PIL import Image

def extract_mrz_from_image(image):
    """Try multiple rotations until MRZ is found."""
    pil_img = Image.fromarray(image)
    
    for angle in [0, 90, 180, 270]:
        rotated = np.array(pil_img.rotate(angle, expand=True))
        mrz = read_mrz(rotated)
        if mrz:
            return mrz.to_dict(), rotated
    
    return None, image

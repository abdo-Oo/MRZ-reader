import numpy as np
from passporteye import read_mrz
from PIL import Image

def extract_mrz_from_image(image):
    """
    Rotate image using PIL only (no OpenCV) and try reading MRZ.
    Works on Streamlit Cloud.
    """
    pil_img = Image.fromarray(image)

    rotations = [0, 90, 180, 270]

    for angle in rotations:
        rotated = pil_img.rotate(angle, expand=True)
        rotated_np = np.array(rotated)

        mrz = read_mrz(rotated_np)
        if mrz:
            return mrz.to_dict(), rotated_np

    return None, image

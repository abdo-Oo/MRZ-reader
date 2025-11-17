import numpy as np
from passporteye import read_mrz
from PIL import Image, ImageFilter

def preprocess_for_mrz(image):
    """
    Improve MRZ detection dramatically by:
    - Upscaling image
    - Converting to grayscale
    - Sharpening the text
    """
    pil = Image.fromarray(image)

    # 1) Upscale (PassportEye needs big MRZ region)
    pil = pil.resize((pil.width * 2, pil.height * 2), Image.LANCZOS)

    # 2) Convert to grayscale
    pil = pil.convert("L")

    # 3) Sharpen edges for OCR
    pil = pil.filter(ImageFilter.SHARPEN)

    return np.array(pil).astype("uint8")


def extract_mrz_from_image(image):
    """
    Attempts MRZ extraction at 4 rotations with enhanced preprocessing.
    """
    rotations = [0, 90, 180, 270]

    for angle in rotations:
        # Rotate via PIL
        pil_rot = Image.fromarray(image).rotate(angle, expand=True)
        rot_np = np.array(pil_rot).astype("uint8")

        # Preprocess for MRZ
        prep = preprocess_for_mrz(rot_np)

        try:
            mrz = read_mrz(prep, save_roi=False)
            if mrz:
                return mrz.to_dict(), prep
        except Exception:
            continue

    # Nothing found
    return None, image

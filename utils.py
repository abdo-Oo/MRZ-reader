import pytesseract
import cv2
from pdf2image import convert_from_path
from PIL import Image
import numpy as np

def extract_mrz_from_image(image):
    """
    Extract MRZ lines using OCR + preprocessing
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Enhance MRZ region
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)

    # OCR
    config = "--oem 1 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<"
    raw = pytesseract.image_to_string(thresh, config=config)

    # Clean output
    lines = [line.strip() for line in raw.split("\n") if line.strip()]
    mrz_lines = [l for l in lines if len(l) >= 30 and "<" in l]

    if len(mrz_lines) >= 2:
        return mrz_lines[0] + "\n" + mrz_lines[1]
    else:
        raise ValueError("MRZ could not be detected.")


def load_image(file):
    """
    Detect if PDF or image and return OpenCV image
    """
    if file.filename.lower().endswith(".pdf"):
        pages = convert_from_path(file.file)
        img = pages[-1]                  # Passport MRZ usually last page
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    else:
        # Regular image
        file_bytes = np.asarray(bytearray(file.file.read()), dtype=np.uint8)
        return cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

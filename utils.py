import cv2
import numpy as np
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
from mrz.checker.td3 import TD3CodeChecker


def pdf_to_image(file_bytes):
    pages = convert_from_bytes(file_bytes)
    return pages[0]


def preprocess_for_ocr(pil_image):
    """Convert to grayscale, increase contrast, and threshold."""
    img = np.array(pil_image.convert("L"))  # grayscale
    img = cv2.equalizeHist(img)             # improve contrast
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return Image.fromarray(img)


def extract_mrz_text(image):
    """Crop bottom ~25%, preprocess, and extract text."""
    width, height = image.size
    mrz_box = (0, int(height * 0.75), width, height)
    mrz_region = image.crop(mrz_box)

    mrz_region = preprocess_for_ocr(mrz_region)

    custom_oem_psm_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ<0123456789'
    mrz_text = pytesseract.image_to_string(mrz_region, config=custom_oem_psm_config)
    mrz_text = "".join(mrz_text.split())  # remove spaces/newlines
    return mrz_text


def parse_mrz_data(mrz_text):
    try:
        mrz = TD3CodeChecker(mrz_text)
        return {
            "first_name": mrz.names,
            "last_name": mrz.surname,
            "document_number": mrz.number
        }
    except Exception:
        return None


def generate_docs_code(last_name, first_name, doc_number):
    return f"YY{last_name.upper()}/{first_name.upper()}/{doc_number.upper()}"

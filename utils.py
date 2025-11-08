import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
from mrz.checker.td3 import TD3CodeChecker  # correct class for passports (TD3 format)

def pdf_to_image(file_bytes):
    pages = convert_from_bytes(file_bytes)
    return pages[0]

def extract_mrz_text(image):
    width, height = image.size
    mrz_box = (0, int(height * 0.75), width, height)
    mrz_region = image.crop(mrz_box)
    mrz_text = pytesseract.image_to_string(mrz_region, config="--psm 6")
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

import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
from passporteye import read_mrz

# Convert PDF to image (first page)
def pdf_to_image(file_bytes):
    pages = convert_from_bytes(file_bytes)
    return pages[0]  # usually the passport info page

# Extract MRZ information
def extract_mrz(image):
    mrz = read_mrz(image)
    if mrz is None:
        return None
    return mrz.to_dict()

# OCR fallback to extract text from image
def extract_text(image):
    text = pytesseract.image_to_string(image)
    return text

# Generate Amadeus DOCS code using "YY" instead of airline code
def generate_docs_code(last_name, first_name, doc_number):
    last_name = last_name.replace(" ", "").upper()
    first_name = first_name.replace(" ", "").upper()
    doc_number = doc_number.replace(" ", "").upper()
    return f"YY{last_name}/{first_name}/{doc_number}"

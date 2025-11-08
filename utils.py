import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from passporteye import read_mrz

# Convert PDF to image
def pdf_to_image(file_path):
    pages = convert_from_path(file_path)
    return pages[0]  # take the first page (usually passport info page)

# Extract MRZ info
def extract_mrz(image):
    mrz = read_mrz(image)
    if mrz is None:
        return None
    return mrz.to_dict()

# OCR to extract text (fallback if MRZ fails)
def extract_text(image):
    text = pytesseract.image_to_string(image)
    return text

# Generate Amadeus DOCS code using "YY"
def generate_docs_code(last_name, first_name, doc_number):
    # Format: YY + last_name + first_name + doc_number
    last_name = last_name.replace(" ", "").upper()
    first_name = first_name.replace(" ", "").upper()
    doc_number = doc_number.replace(" ", "").upper()
    return f"YY{last_name}/{first_name}/{doc_number}"

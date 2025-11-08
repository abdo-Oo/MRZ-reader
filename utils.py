import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
from mrz.parser import parse_mrz

# Convert PDF bytes to image (first page)
def pdf_to_image(file_bytes):
    pages = convert_from_bytes(file_bytes)
    return pages[0]

# Extract MRZ text using pytesseract
def extract_mrz_text(image):
    # Crop bottom ~15% of passport page where MRZ usually is
    width, height = image.size
    mrz_box = (0, int(height*0.75), width, height)
    mrz_region = image.crop(mrz_box)

    mrz_text = pytesseract.image_to_string(mrz_region, config="--psm 6")
    mrz_text = mrz_text.replace(" ", "").replace("\n", "")
    return mrz_text

# Parse MRZ text into structured data
def parse_mrz_data(mrz_text):
    try:
        mrz = parse_mrz(mrz_text)
        return {
            "first_name": mrz.names,
            "last_name": mrz.surname,
            "document_number": mrz.number
        }
    except:
        return None

# Generate Amadeus DOCS code using "YY"
def generate_docs_code(last_name, first_name, doc_number):
    last_name = last_name.replace(" ", "").upper()
    first_name = first_name.replace(" ", "").upper()
    doc_number = doc_number.replace(" ", "").upper()
    return f"YY{last_name}/{first_name}/{doc_number}"

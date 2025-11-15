from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from passporteye import read_mrz
from pdf2image import convert_from_bytes
import cv2
import numpy as np
from PIL import Image
import io

app = FastAPI(title="MRZ/Passport Extractor")

def preprocess_image(image: Image.Image):
    """
    Preprocess the image for MRZ detection:
    - Converts to grayscale
    - Rotates if width < height
    - Applies thresholding
    """
    img = np.array(image)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # Rotate if portrait (height > width)
    if gray.shape[0] > gray.shape[1]:
        gray = cv2.rotate(gray, cv2.ROTATE_90_CLOCKWISE)
    
    # Thresholding to improve OCR
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return Image.fromarray(thresh)

def extract_mrz_from_image(image: Image.Image):
    """
    Extract MRZ data using PassportEye
    """
    preprocessed = preprocess_image(image)
    mrz = read_mrz(np.array(preprocessed))
    if mrz is None:
        return None
    return mrz.to_dict()

def parse_names(mrz_data):
    """
    Parse first, middle, last names from MRZ
    """
    last_name = mrz_data.get("surname", "")
    full_names = mrz_data.get("names", "")
    names_split = full_names.split()
    first_name = names_split[0] if len(names_split) > 0 else ""
    middle_name = " ".join(names_split[1:]) if len(names_split) > 1 else ""
    return first_name, middle_name, last_name

def generate_amadeus_command(mrz_data, first_name, last_name):
    """
    Generate Amadeus command from MRZ data
    Format: SRCOS YY HK1-NAT-PASSP-NAT-DOB-GENDER-EXP-LAST/FIRST
    """
    return f"SRCOS YY HK1-{mrz_data.get('nationality')}-{mrz_data.get('number')}-" \
           f"{mrz_data.get('nationality')}-{mrz_data.get('date_of_birth')}-" \
           f"{mrz_data.get('sex')}-{mrz_data.get('expiration_date')}-{last_name}/{first_name}"

@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    """
    Endpoint to extract MRZ from uploaded image/PDF
    """
    content = await file.read()
    
    # Handle PDFs
    if file.filename.lower().endswith(".pdf"):
        pages = convert_from_bytes(content)
        if not pages:
            return JSONResponse(status_code=400, content={"error": "No pages found in PDF"})
        image = pages[0]  # take first page
    else:
        # Handle image
        image = Image.open(io.BytesIO(content))
    
    mrz_data = extract_mrz_from_image(image)
    if mrz_data is None:
        return JSONResponse(status_code=400, content={"error": "MRZ could not be detected"})
    
    first_name, middle_name, last_name = parse_names(mrz_data)
    amadeus_command = generate_amadeus_command(mrz_data, first_name, last_name)
    
    return {
        "mrz_data": mrz_data,
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "amadeus_command": amadeus_command
    }

import os
from pdf2image import convert_from_path
from PIL import Image
from passporteye import read_mrz


def pdf_to_image(pdf_path):
    """Convert first page of PDF to an image."""
    images = convert_from_path(pdf_path, dpi=300)
    if images:
        img_path = "temp_passport.jpg"
        images[0].save(img_path, "JPEG")
        return img_path
    return None


def extract_mrz_data(image_path):
    """Extract MRZ data from passport image using PassportEye."""
    mrz = read_mrz(image_path, save_roi=False)
    if mrz is None:
        return None

    data = mrz.to_dict()
    first_name = data.get("names", "")
    last_name = data.get("surname", "")
    passport_no = data.get("number", "")
    nationality = data.get("nationality", "")
    birth_date = data.get("date_of_birth", "")
    gender = data.get("sex", "")
    expiry_date = data.get("expiration_date", "")

    return {
        "first_name": first_name,
        "last_name": last_name,
        "passport_number": passport_no,
        "nationality": nationality,
        "birth_date": birth_date,
        "gender": gender,
        "expiry_date": expiry_date,
    }


def generate_docs_code(data):
    """Generate Amadeus DOCS line with YY airline code placeholder."""
    if not data:
        return None

    # Format: YY HK1-P/US/DOE/JOHN/M/01JAN90/US/12DEC30/XXXXXXXXX
    return (
        f"YY HK1-P/{data.get('nationality','')}/"
        f"{data.get('last_name','')}/{data.get('first_name','')}/"
        f"{data.get('gender','')}/{data.get('birth_date','')}/"
        f"{data.get('nationality','')}/{data.get('expiry_date','')}/"
        f"{data.get('passport_number','')}"
    )

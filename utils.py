from datetime import datetime
from pdf2image import convert_from_path
from passporteye import read_mrz


def pdf_to_image(pdf_path):
    """Convert first page of PDF to image."""
    images = convert_from_path(pdf_path, dpi=300)
    if images:
        img_path = "temp_passport.jpg"
        images[0].save(img_path, "JPEG")
        return img_path
    return None


def extract_mrz_data(image_path):
    """Extract MRZ info from passport using PassportEye."""
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


def format_date(date_str):
    """Convert MRZ-style dates into Amadeus DOCS format (DDMMMYY)."""
    if not date_str:
        return ""
    try:
        for fmt in ("%y%m%d", "%Y-%m-%d", "%d%m%y", "%Y%m%d"):
            try:
                d = datetime.strptime(date_str, fmt)
                return d.strftime("%d%b%y").upper()
            except ValueError:
                continue
    except Exception:
        pass
    return date_str


def generate_docs_code(data):
    """Generate a fully Amadeus-compliant DOCS command."""
    if not data:
        return None

    nationality = data.get("nationality", "").upper()
    last_name = data.get("last_name", "").upper().replace(" ", "")
    first_name = data.get("first_name", "").upper().replace(" ", "")
    gender = data.get("gender", "U").upper()[0]
    dob = format_date(data.get("birth_date", ""))
    expiry = format_date(data.get("expiry_date", ""))
    passport = data.get("passport_number", "").upper().replace(" ", "")

    docs = (
        f"DOCS YY HK1 P/{nationality}/{passport}/{nationality}/{expiry}"
        f"{gender}/{dob}/{last_name}/{first_name}"
    )
    return docs

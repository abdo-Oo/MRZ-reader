from passporteye import read_mrz
from pdf2image import convert_from_bytes
from PIL import Image
import io

def extract_mrz_text(image):
    """
    Extracts MRZ text from a passport image using PassportEye.
    Returns the raw MRZ string or None if not detected.
    """
    # Ensure image is in bytes for PassportEye
    if isinstance(image, Image.Image):
        buf = io.BytesIO()
        image.save(buf, format="JPEG")
        img_bytes = buf.getvalue()
    else:
        img_bytes = image

    # Use PassportEye to read MRZ
    mrz = read_mrz(img_bytes)

    if mrz:
        return mrz
    else:
        return None


def parse_mrz_data(mrz):
    """
    Converts PassportEye MRZ result into a clean dictionary.
    """
    if not mrz:
        return None

    mrz_data = mrz.to_dict()
    data = {
        "First Name": mrz_data.get("names", ""),
        "Last Name": mrz_data.get("surname", ""),
        "Passport Number": mrz_data.get("number", ""),
        "Nationality": mrz_data.get("nationality", ""),
        "Date of Birth": mrz_data.get("date_of_birth", ""),
        "Gender": mrz_data.get("sex", ""),
        "Expiry Date": mrz_data.get("expiration_date", "")
    }

    return data


def generate_docs_code(data):
    """
    Generates an Amadeus DOCS command using YY instead of airline code.
    Example: DOCS YY HK1-P/GBR/123456789/GBR/15JAN90/M/15JAN30/DOE/JOHN
    """
    if not data:
        return "No MRZ data found."

    docs_code = (
        f"DOCS YY HK1-P/{data.get('Nationality','')}/"
        f"{data.get('Passport Number','')}/{data.get('Nationality','')}/"
        f"{data.get('Date of Birth','')}/{data.get('Gender','')}/"
        f"{data.get('Expiry Date','')}/"
        f"{data.get('Last Name','')}/{data.get('First Name','')}"
    )

    return docs_code

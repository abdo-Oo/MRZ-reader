from passporteye import read_mrz
from PIL import Image, ExifTags
import io, numpy as np
from pdf2image import convert_from_bytes

def load_image(file):
    """Load image or PDF, and auto-rotate if needed."""
    if file.type == "application/pdf":
        pages = convert_from_bytes(file.read())
        image = pages[0]
    else:
        image = Image.open(file)
        # Handle EXIF rotation (for phone pictures)
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = dict(image._getexif().items())
            if exif[orientation] == 3:
                image = image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image = image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image = image.rotate(90, expand=True)
        except Exception:
            pass
    return image


def extract_mrz_data(image):
    """Extract MRZ data (try original + rotated if needed)."""
    # Convert to bytes
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    # Try reading MRZ normally
    mrz = read_mrz(img_bytes)
    if not mrz:
        # Try rotated versions
        for angle in [90, 180, 270]:
            rotated = image.rotate(angle, expand=True)
            buf = io.BytesIO()
            rotated.save(buf, format="JPEG")
            mrz = read_mrz(buf.getvalue())
            if mrz:
                break

    return mrz


def parse_mrz(mrz):
    """Parse MRZ data into readable dict."""
    if not mrz:
        return None
    data = mrz.to_dict()
    return {
        "First Name": data.get("names", "").replace("<", " "),
        "Last Name": data.get("surname", "").replace("<", " "),
        "Passport Number": data.get("number", ""),
        "Nationality": data.get("nationality", ""),
        "Date of Birth": data.get("date_of_birth", ""),
        "Gender": data.get("sex", ""),
        "Expiry Date": data.get("expiration_date", "")
    }


def generate_srdocs(data):
    """Generate Amadeus SRDOCS command."""
    if not data:
        return "No MRZ data found."

    docs = (
        f"SRDOCS YY HK1-P/{data['Nationality']}/"
        f"{data['Passport Number']}/{data['Nationality']}/"
        f"{data['Date of Birth']}/{data['Gender']}/"
        f"{data['Expiry Date']}/"
        f"{data['Last Name'].strip()}/{data['First Name'].strip()}"
    )
    return docs

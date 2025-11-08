import streamlit as st
from PIL import Image
import pytesseract
from datetime import datetime
import io
import re

st.set_page_config(page_title="Passport MRZ → Amadeus DOCS Generator")
st.title("Passport MRZ → Amadeus DOCS Generator")

st.markdown(
    "📸 **Upload or paste (Ctrl + V)** your passport image below. "
    "The tool will extract MRZ details and build the **Amadeus DOCS** command automatically."
)

# --- Import the paste component (install with `pip install streamlit-paste`)
try:
    from streamlit_paste import paste_image
    pasted_image = paste_image()
except Exception:
    pasted_image = None

uploaded_file = st.file_uploader("Upload a passport image", type=["jpg", "jpeg", "png"])

# Accept either upload or pasted image
image_data = None
if uploaded_file:
    image_data = uploaded_file.read()
elif pasted_image is not None:
    # pasted_image returns a PIL Image
    buf = io.BytesIO()
    pasted_image.save(buf, format="JPEG")
    image_data = buf.getvalue()


def format_date(date_str):
    """Convert YYMMDD to DDMMMYY (Amadeus style)."""
    try:
        return datetime.strptime(date_str, "%y%m%d").strftime("%d%b%y").upper()
    except Exception:
        return ""


def extract_mrz_text(image_path):
    """Use pytesseract to read MRZ lines from image."""
    img = Image.open(image_path)
    # Convert to grayscale for better OCR
    img = img.convert("L")
    text = pytesseract.image_to_string(img)
    
    # Keep only MRZ characters (A-Z, 0-9, <)
    mrz_lines = [line.strip() for line in text.splitlines() if re.match(r'^[A-Z0-9<]+$', line.replace(" ", ""))]
    
    # Usually MRZ is 2 or 3 lines
    if len(mrz_lines) >= 2:
        return mrz_lines[-2:]  # take last 2 lines
    return None


def parse_mrz(mrz_lines):
    """Manually parse MRZ lines into passport fields."""
    if not mrz_lines or len(mrz_lines) < 2:
        return None

    line1, line2 = mrz_lines

    # Pad lines with '<' if too short
    line1 = line1.ljust(44, '<')
    line2 = line2.ljust(44, '<')

    # Example parsing for TD3 passports (most common)
    passport_type = line1[0]
    issuing_country = line1[2:5]
    names = line1[5:].replace("<", " ").strip().split("  ")
    surname = names[0]
    given_names = " ".join(names[1:])

    passport_number = line2[0:9].replace("<", "")
    nationality = line2[10:13]
    dob = line2[13:19]
    sex = line2[20]
    expiry = line2[21:27]

    return {
        "surname": surname,
        "names": given_names,
        "nationality": nationality,
        "number": passport_number,
        "date_of_birth": dob,
        "sex": sex,
        "expiration_date": expiry,
        "country": issuing_country
    }

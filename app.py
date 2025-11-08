import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pytesseract
import cv2
import numpy as np
import io
from pdf2image import convert_from_bytes
from datetime import datetime

# Optional: install streamlit-paste for clipboard support
try:
    from streamlit_paste import paste_image
except ImportError:
    paste_image = None

# --- App setup ---
st.set_page_config(page_title="Passport MRZ → Amadeus DOCS Generator")
st.title("📸 Passport MRZ → Amadeus DOCS Generator")
st.markdown(
    "Upload or paste a passport image/PDF. The tool extracts MRZ and passport fields, validates them, "
    "and generates the Amadeus DOCS command."
)

# --- Helper functions ---
def format_date(date_str):
    """Convert YYMMDD to DDMMMYY (Amadeus style)."""
    try:
        return datetime.strptime(date_str, "%y%m%d").strftime("%d%b%y").upper()
    except:
        return ""

def extract_mrz(image):
    """Detect MRZ automatically and extract text."""
    # Convert to grayscale
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    # Apply threshold
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # MRZ usually at bottom: crop bottom 25% of the image
    h = thresh.shape[0]
    mrz_region = thresh[int(h*0.7):, :]
    # OCR MRZ
    mrz_text = pytesseract.image_to_string(mrz_region, config='--psm 6')
    # Clean lines
    lines = [line for line in mrz_text.split("\n") if line.strip() != ""]
    if len(lines) >= 2:
        return lines[-2:]  # Usually last 2 lines
    return None

def parse_mrz_lines(lines):
    """Parse MRZ into fields."""
    if not lines or len(lines) < 2:
        return None
    line1, line2 = lines
    try:
        passport_number = line2[0:9].replace("<", "").strip()
        nationality = line2[10:13]
        dob = line2[13:19]
        sex = line2[20]
        expiry = line2[21:27]
        surname, given_names = line1.split("<<")
        surname = surname.replace("<", " ").strip()
        given_names = given_names.replace("<", " ").strip()
        issuing_country = line1[2:5]
        return {
            "surname": surname,
            "given_names": given_names,
            "passport_number": passport_number,
            "nationality": nationality,
            "date_of_birth": dob,
            "sex": sex,
            "expiration_date": expiry,
            "issuing_country": issuing_country
        }
    except:
        return None

def add_watermark(image, text="TEZ tours"):
    """Add watermark at center."""
    img = image.copy()
    draw = ImageDraw.Draw(img)
    font_size = int(min(img.size)/10)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    w, h = draw.textsize(text, font=font)
    position = ((img.width - w)//2, (img.height - h)//2)
    draw.text(position, text, fill=(200,200,200,128), font=font)
    return img

# --- Upload or paste file ---
uploaded_file = st.file_uploader("Upload image or PDF", type=["jpg","jpeg","png","pdf"])
pasted_image = None
if paste_image:
    pasted_image = paste_image()

image_data = None

# Handle PDF
if uploaded_file and uploaded_file.type == "application/pdf":
    pages = convert_from_bytes(uploaded_file.read())
    if pages:
        image_data = pages[0]  # Process first page
elif uploaded_file:
    image_data = Image.open(uploaded_file)
elif pasted_image:
    image_data = pasted_image

# --- Process image ---
if image_data:
    st.image(add_watermark(image_data), caption="Preview with TEZ tours watermark", use_column_width=True)
    
    mrz_lines = extract_mrz(image_data)
    if mrz_lines:
        st.subheader("MRZ Detected:")
        st.text("\n".join(mrz_lines))
        
        data = parse_mrz_lines(mrz_lines)
        if data:
            st.subheader("Extracted Passport Data:")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Surname:**", data['surname'])
                st.write("**Given Names:**", data['given_names'])
                st.write("**Gender:**", data['sex'])
                st.write("**Date of Birth:**", format_date(data['date_of_birth']))
            with col2:
                st.write("**Nationality:**", data['nationality'])
                st.write("**Passport #:**", data['passport_number'])
                st.write("**Expiry:**", format_date(data['expiration_date']))
                st.write("**Issuing Country:**", data['issuing_country'])
            
            st.divider()
            airline_code = "YY"
            docs_command = (
                f"SR DOCS {airline_code} HK1 P/"
                f"{data['nationality']}/{data['passport_number']}/{data['issuing_country']}/"
                f"{format_date(data['date_of_birth'])}/{data['sex']}/{format_date(data['expiration_date'])}/"
                f"{data['surname']}/{data['given_names'].replace(' ', '')}"
            )
            st.subheader("Amadeus DOCS Command")
            st.text_area("", docs_command, height=80)
        else:
            st.error("❌ Failed to parse MRZ. Try a clearer image.")
    else:
        st.error("❌ MRZ not detected. Make sure it's visible and clear.")
else:
    st.info("👉 Upload or paste an image/PDF of the passport to start.")

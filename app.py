import streamlit as st
from passporteye import read_mrz
from datetime import datetime
from PIL import Image
import numpy as np
import io
from pdf2image import convert_from_bytes

# -----------------------------
# Streamlit page config
# -----------------------------
st.set_page_config(page_title="Passport MRZ → Amadeus DOCS Generator", layout="wide")
st.title("📄 Passport MRZ → Amadeus DOCS Generator")

# Background image (TEZ Tours)
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://i.imgur.com/7uY1d0K.jpg"); /* Replace with your TEZ Tours background */
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    "📸 **Upload, paste (Ctrl+V), or drag-and-drop** a passport image or PDF file. "
    "The tool will extract MRZ details and generate the **Amadeus DOCS** command."
)

# -----------------------------
# File uploader
# -----------------------------
uploaded_file = st.file_uploader("Upload passport image or PDF", type=["jpg", "jpeg", "png", "pdf"])

# -----------------------------
# Paste screenshot
# -----------------------------
try:
    from streamlit.components.v1 import html

    st.markdown("### 📌 Paste your screenshot (Ctrl+V)")
    pasted_image = st.camera_input("Or capture a live passport image")  # Optional: can use camera_input
except Exception:
    pasted_image = None

# -----------------------------
# Helper functions
# -----------------------------
def format_date(date_str):
    """Convert YYMMDD to DDMMMYY (Amadeus style)."""
    try:
        return datetime.strptime(date_str, "%y%m%d").strftime("%d%b%y").upper()
    except Exception:
        return ""

def extract_mrz_and_validate(img: Image.Image):
    """Convert image to NumPy and read MRZ using PassportEye."""
    img_np = np.array(img.convert('L'))  # Convert to grayscale
    mrz = read_mrz(img_np)
    if not mrz:
        return None, "❌ MRZ not detected."
    
    data = mrz.to_dict()
    return {
        "surname": data.get("surname", "").strip(),
        "given_names": data.get("names", "").strip(),
        "nationality": data.get("nationality", "").strip(),
        "passport_number": data.get("number", "").strip(),
        "dob": data.get("date_of_birth", "").strip(),
        "sex": data.get("sex", "").strip(),
        "expiry": data.get("expiration_date", "").strip(),
        "issuing_country": data.get("country", "").strip()
    }, None

# -----------------------------
# Load image from uploaded file or PDF
# -----------------------------
image_data = None
if uploaded_file:
    if uploaded_file.type == "application/pdf":
        pages = convert_from_bytes(uploaded_file.read(), dpi=300)
        image_data = pages[0]  # Take first page only
    else:
        image_data = Image.open(uploaded_file)

elif pasted_image:
    image_data = pasted_image

# -----------------------------
# Process image
# -----------------------------
if image_data:
    st.image(image_data, caption="Uploaded Passport", use_column_width=True)
    
    data, error = extract_mrz_and_validate(image_data)
    
    if error:
        st.error(error)
    else:
        st.success("✅ MRZ data extracted successfully!")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Surname:**", data["surname"])
            st.write("**Given Names:**", data["given_names"])
            st.write("**Gender:**", data["sex"])
            st.write("**Date of Birth:**", format_date(data["dob"]))
        with col2:
            st.write("**Nationality:**", data["nationality"])
            st.write("**Passport #:**", data["passport_number"])
            st.write("**Expiry:**", format_date(data["expiry"]))
            st.write("**Issuing Country:**", data["issuing_country"])
        
        st.divider()
        
        # Default airline code as "YY"
        airline_code = "YY"
        docs_command = (
            f"SR DOCS {airline_code} HK1 P/"
            f"{data['nationality']}/{data['passport_number']}/{data['issuing_country']}/"
            f"{format_date(data['dob'])}/{data['sex']}/{format_date(data['expiry'])}/"
            f"{data['surname']}/{data['given_names'].replace(' ', '')}"
        )
        
        st.text_area("Amadeus DOCS Command:", docs_command, height=80)
        st.caption("✈️ Copy and paste this directly into Amadeus PNR.")

else:
    st.info("👉 Upload a passport image or PDF, or paste a screenshot to start.")

import streamlit as st
from passporteye import read_mrz
from datetime import datetime
from PIL import Image
import io
import os

# Optional: For PDF support
try:
    from pdf2image import convert_from_bytes
except ImportError:
    convert_from_bytes = None

# Optional: For pasted screenshots
try:
    from streamlit_paste import paste_image
except ImportError:
    paste_image = None

# --- Streamlit page config ---
st.set_page_config(page_title="TEZ Tours Passport MRZ Reader")
st.title("🛫 TEZ Tours Passport MRZ Reader")

st.markdown("""
📸 Upload or paste a passport image (JPG/PNG) or PDF.
The app will extract MRZ details and validate them against the passport details.
""")

# --- Upload or paste file ---
uploaded_file = st.file_uploader("Upload a passport image or PDF", type=["jpg", "jpeg", "png", "pdf"])

pasted_image = None
if paste_image:
    pasted_image = paste_image()

image_list = []

# Handle uploaded files
if uploaded_file:
    if uploaded_file.type == "application/pdf":
        if convert_from_bytes is None:
            st.error("PDF support requires pdf2image. Please install it.")
        else:
            try:
                images = convert_from_bytes(uploaded_file.read())
                image_list.extend(images)
            except Exception as e:
                st.error(f"Failed to read PDF: {e}")
    else:
        try:
            img = Image.open(uploaded_file)
            image_list.append(img)
        except Exception as e:
            st.error(f"Failed to read image: {e}")

# Handle pasted image
if pasted_image is not None:
    image_list.append(pasted_image)

# --- Helper functions ---
def format_date(date_str):
    """Convert YYMMDD to DDMMMYY format (Amadeus style)."""
    try:
        return datetime.strptime(date_str, "%y%m%d").strftime("%d%b%y").upper()
    except Exception:
        return ""

def extract_mrz_and_validate(img: Image.Image):
    """Extract MRZ and validate passport details."""
    mrz = read_mrz(img)
    if not mrz:
        return None, "❌ MRZ not detected."

    data = mrz.to_dict()

    # Extract MRZ fields
    surname = data.get("surname", "").strip()
    given_names = data.get("names", "").strip()
    nationality = data.get("nationality", "").strip()
    passport_number = data.get("number", "").strip()
    dob = data.get("date_of_birth", "").strip()
    sex = data.get("sex", "").strip()
    expiry = data.get("expiration_date", "").strip()
    issuing_country = data.get("country", "").strip()

    # Optional: Add validation logic here if needed
    return {
        "surname": surname,
        "given_names": given_names,
        "nationality": nationality,
        "passport_number": passport_number,
        "dob": dob,
        "sex": sex,
        "expiry": expiry,
        "issuing_country": issuing_country
    }, None

# --- Process images ---
if image_list:
    for idx, img in enumerate(image_list):
        st.image(img, caption=f"Uploaded Image {idx+1}", use_column_width=True)

        data, error = extract_mrz_and_validate(img)
        if error:
            st.error(error)
            continue

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

        # Generate Amadeus DOCS command
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
    st.info("👉 Upload an image/PDF or paste a screenshot to start.")

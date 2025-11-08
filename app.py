import streamlit as st
from passporteye import read_mrz
from datetime import datetime
from PIL import Image
import io
import tempfile

# For PDF conversion
from pdf2image import convert_from_bytes

# --- Page Settings ---
st.set_page_config(
    page_title="Passport MRZ → Amadeus DOCS Generator",
    page_icon="✈️",
    layout="centered"
)

# --- Branding Header ---
col1, col2 = st.columns([1, 4])
with col1:
    st.image("logo.png", width=100)
with col2:
    st.markdown(
        """
        <h1 style='margin-bottom:0;'>🌍 CompanyName</h1>
        <p style='font-size:18px; margin-top:0; color:#555;'>
        Passport MRZ → Amadeus DOCS Generator
        </p>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

st.markdown(
    "📸 **Upload or paste (Ctrl + V)** your passport image or PDF below. "
    "The tool extracts MRZ details and generates the **Amadeus DOCS** command automatically."
)

# --- Paste or upload section ---
try:
    from streamlit_paste import paste_image
    pasted_image = paste_image()
except Exception:
    pasted_image = None

uploaded_file = st.file_uploader("Upload passport image or PDF", type=["jpg", "jpeg", "png", "pdf"])

# --- Handle uploaded or pasted file ---
image_data = None

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        # Convert PDF to image
        pdf_bytes = uploaded_file.read()
        images = convert_from_bytes(pdf_bytes)
        # Use the first page of the PDF
        if images:
            buf = io.BytesIO()
            images[0].save(buf, format="JPEG")
            image_data = buf.getvalue()
    else:
        image_data = uploaded_file.read()

elif pasted_image is not None:
    buf = io.BytesIO()
    pasted_image.save(buf, format="JPEG")
    image_data = buf.getvalue()

# --- Helper function ---
def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%y%m%d").strftime("%d%b%y").upper()
    except Exception:
        return ""

# --- MRZ Extraction ---
if image_data:
    # Save temporary image
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_file.write(image_data)
        temp_file_path = temp_file.name

    mrz = read_mrz(temp_file_path)

    if mrz:
        data = mrz.to_dict()

        surname = data.get('surname', '').strip()
        given_names = data.get('names', '').strip()
        nationality = data.get('nationality', '').strip()
        passport_number = data.get('number', '').strip()
        dob = data.get('date_of_birth', '').strip()
        sex = data.get('sex', '').strip()
        expiry = data.get('expiration_date', '').strip()
        issuing_country = data.get('country', '').strip()

        st.success("✅ MRZ data extracted successfully!")

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Surname:**", surname)
            st.write("**Given Names:**", given_names)
            st.write("**Gender:**", sex)
            st.write("**Date of Birth:**", format_date(dob))
        with col2:
            st.write("**Nationality:**", nationality)
            st.write("**Passport #:**", passport_number)
            st.write("**Expiry:**", format_date(expiry))
            st.write("**Issuing Country:**", issuing_country)

        st.divider()

        # Use YY as default airline code
        airline_code = "YY"
        docs_command = (
            f"SR DOCS {airline_code} HK1 P/"
            f"{nationality}/{passport_number}/{issuing_country}/"
            f"{format_date(dob)}/{sex}/{format_date(expiry)}/"
            f"{surname}/{given_names.replace(' ', '')}"
        )

        st.text_area("Amadeus DOCS Command:", docs_command, height=80)
        st.caption("✈️ Copy and paste this directly into Amadeus PNR.")
    else:
        st.error("❌ Could not read MRZ. Try a clearer passport image or PDF.")
else:
    st.info("👉 Paste (Ctrl + V) or upload a passport image or PDF to start.")

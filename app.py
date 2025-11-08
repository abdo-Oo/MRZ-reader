import streamlit as st
from passporteye import read_mrz
from datetime import datetime
from PIL import Image
import io

# --- Page settings ---
st.set_page_config(
    page_title="Passport MRZ → Amadeus DOCS Generator",
    page_icon="✈️",
    layout="centered"
)

# --- Custom header with company logo ---
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
    "📸 **Upload or paste (Ctrl + V)** your passport image below. "
    "The system will extract MRZ details and automatically generate the **Amadeus DOCS** command."
)

# --- Paste or upload section ---
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
    buf = io.BytesIO()
    pasted_image.save(buf, format="JPEG")
    image_data = buf.getvalue()

# --- Utility functions ---
def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%y%m%d").strftime("%d%b%y").upper()
    except Exception:
        return ""

# --- MRZ Extraction & Command Generation ---
if image_data:
    with open("temp.jpg", "wb") as f:
        f.write(image_data)

    mrz = read_mrz("temp.jpg")

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

        airline_code = "YY"
        docs_command = (
            f"SR DOCS {airline_code} HK1 P/"
            f"{nationality}/{passport_number}/{issuing_country}/"
            f"{format_date(dob)}/{sex}/{format_date(expiry)}/"
            f"{surname}/{given_names.replace(' ', '')}"
        )

        st.text_area("Amadeus DOCS Command:", docs_command, height=80)
        st.caption("✈️ Copy this into the PNR in Amadeus.")
    else:
        st.error("❌ Could not read MRZ. Try a clearer passport image.")
else:
    st.info("👉 Paste (Ctrl + V) or upload a passport image to start.")

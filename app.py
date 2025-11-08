import streamlit as st
from passporteye import read_mrz
from datetime import datetime
from PIL import Image
import io

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

        # Default airline code as "YY"
        airline_code = "YY"

        # Generate the Amadeus DOCS command
        docs_command = (
            f"SR DOCS {airline_code} HK1 P/"
            f"{nationality}/{passport_number}/{issuing_country}/"
            f"{format_date(dob)}/{sex}/{format_date(expiry)}/"
            f"{surname}/{given_names.replace(' ', '')}"
        )

        st.text_area("Amadeus DOCS Command:", docs_command, height=80)
        st.caption("✈️ Copy and paste this directly into Amadeus PNR.")
    else:
        st.error("❌ Could not read MRZ. Try a clearer passport image.")
else:
    st.info("👉 Paste (Ctrl + V) or upload a passport image to start.")

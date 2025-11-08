import streamlit as st
from PIL import Image
import io
from mrz.reader import read_mrz
import tempfile

# Optional: Paste image support
try:
    from streamlit_paste import paste_image
    pasted_image = paste_image()
except Exception:
    pasted_image = None

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
    "📸 **Upload or paste (Ctrl + V)** your passport image below. "
    "The tool extracts MRZ details and generates the **Amadeus DOCS** command automatically."
)

# --- Upload image ---
uploaded_file = st.file_uploader("Upload passport image", type=["jpg", "jpeg", "png"])

# --- Handle image from upload or paste ---
image_data = None

if uploaded_file:
    image_data = uploaded_file.read()
elif pasted_image is not None:
    buf = io.BytesIO()
    pasted_image.save(buf, format="JPEG")
    image_data = buf.getvalue()

# --- Helper function ---
def format_date(date_str):
    try:
        return f"{date_str[0:2]}{date_str[2:4]}{date_str[4:6]}"  # simple DDMMYY placeholder
    except Exception:
        return ""

# --- MRZ Extraction ---
if image_data:
    # Save temporary image
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_file.write(image_data)
        temp_file_path = temp_file.name

    mrz_result = read_mrz(temp_file_path)

    if mrz_result.valid:
        surname = mrz_result.surname.replace("<", " ").strip()
        given_names = mrz_result.given_names.replace("<", " ").strip()
        nationality = mrz_result.nationality.strip()
        passport_number = mrz_result.number.strip()
        dob = mrz_result.date_of_birth.strip()
        sex = mrz_result.sex.strip()
        expiry = mrz_result.expiration_date.strip()
        issuing_country = mrz_result.country.strip()

        st.success("✅ MRZ data extracted successfully!")

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Surname:**", surname)
            st.write("**Given Names:**", given_names)
            st.write("**Gender:**", sex)
            st.write("**Date of Birth:**", dob)
        with col2:
            st.write("**Nationality:**", nationality)
            st.write("**Passport #:**", passport_number)
            st.write("**Expiry:**", expiry)
            st.write("**Issuing Country:**", issuing_country)

        st.divider()

        # Use YY as default airline code
        airline_code = "YY"
        docs_command = (
            f"SR DOCS {airline_code} HK1 P/"
            f"{nationality}/{passport_number}/{issuing_country}/"
            f"{dob}/{sex}/{expiry}/"
            f"{surname}/{given_names.replace(' ', '')}"
        )

        st.text_area("Amadeus DOCS Command:", docs_command, height=80)
        st.caption("✈️ Copy and paste this directly into Amadeus PNR.")

    else:
        st.error("❌ Could not read MRZ. Make sure the passport image is clear.")
else:
    st.info("👉 Paste (Ctrl + V) or upload a passport image to start.")

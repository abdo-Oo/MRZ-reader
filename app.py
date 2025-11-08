import streamlit as st
from datetime import datetime
from PIL import Image
import io
import pytesseract

st.set_page_config(page_title="Passport MRZ → Amadeus DOCS Generator")
st.title("Passport MRZ → Amadeus DOCS Generator")

st.markdown(
    "📸 **Upload or paste (Ctrl + V)** your passport image below. "
    "The tool will extract MRZ details and build the **Amadeus DOCS** command automatically."
)

# --- Paste image component (optional)
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

def format_date(date_str):
    """Convert YYMMDD to DDMMMYY (Amadeus style)."""
    try:
        return datetime.strptime(date_str, "%y%m%d").strftime("%d%b%y").upper()
    except Exception:
        return ""

def parse_mrz(mrz_lines):
    """Manually parse MRZ lines into passport fields."""
    if not mrz_lines or len(mrz_lines) < 2:
        return None

    line1, line2 = mrz_lines

    # Pad lines with '<' if too short
    line1 = line1.ljust(44, '<')
    line2 = line2.ljust(44, '<')

    # Example parsing for TD3 passports
    passport_type = line1[0]
    issuing_country = line1[2:5]
    names = line1[5:].replace("<", " ").strip().split("  ")
    surname = names[0]
    given_names = " ".join(names[1:]) if len(names) > 1 else ""

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

if image_data:
    with open("temp.jpg", "wb") as f:
        f.write(image_data)

    # Convert image to string using pytesseract
    image = Image.open("temp.jpg")
    mrz_text = pytesseract.image_to_string(image, config="--psm 6")
    mrz_lines = [line for line in mrz_text.splitlines() if line.strip() != '']

    # Filter lines that look like MRZ (two lines of ~44 characters)
    mrz_lines = [line for line in mrz_lines if len(line) >= 30]
    if len(mrz_lines) >= 2:
        mrz_lines = mrz_lines[-2:]  # take last two lines as MRZ
        data = parse_mrz(mrz_lines)

             if data:
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
            st.error("❌ Could not parse MRZ. Try a clearer passport image.")
    else:
        st.error("❌ MRZ not detected. Make sure the image clearly shows the MRZ lines.")
else:
    st.info("👉 Paste (Ctrl + V) or upload a passport image to start.")

import streamlit as st
from PIL import Image
import pytesseract
from mrz.base import MRZ
from mrz.checker.td3 import TD3CodeChecker
import re
import io

st.title("MRZ Reader")

st.write("Upload an image of a passport or ID with MRZ lines")

# Upload image
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file is not None:
    try:
        # Handle PDF input
        if uploaded_file.type == "application/pdf":
            from pdf2image import convert_from_bytes
            images = convert_from_bytes(uploaded_file.read())
            image = images[0]  # Only process first page
        else:
            image = Image.open(uploaded_file)

        st.image(image, caption="Uploaded Image", use_column_width=True)

        # OCR to extract text
        mrz_text = pytesseract.image_to_string(image)
        st.text_area("Raw OCR Output", mrz_text, height=150)

        # Filter MRZ-like lines (letters, numbers, <)
        lines = [line for line in mrz_text.split("\n") if re.match(r'^[A-Z0-9<]{10,44}$', line)]
        if len(lines) < 2:
            st.warning("Could not detect MRZ lines. Make sure the image is clear and MRZ is visible.")
        else:
            mrz_code = "\n".join(lines[-2:])  # Usually the last 2 lines
            st.text_area("Detected MRZ", mrz_code, height=100)

            # Parse MRZ using mrz library
            try:
                mrz_obj = MRZ(mrz_code)
                st.write("Parsed MRZ Data:")
                for k, v in mrz_obj.to_dict().items():
                    st.write(f"**{k}**: {v}")
            except Exception as e:
                st.error(f"Error parsing MRZ: {e}")

    except Exception as e:
        st.error(f"Error processing file: {e}")

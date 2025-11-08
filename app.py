import streamlit as st
from PIL import Image
import pytesseract
import re
from pdf2image import convert_from_bytes

st.title("MRZ Reader")

st.write("Upload a passport or ID image (or PDF) containing MRZ lines.")

# File upload
uploaded_file = st.file_uploader("Choose an image or PDF...", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file is not None:
    try:
        # Handle PDFs
        if uploaded_file.type == "application/pdf":
            images = convert_from_bytes(uploaded_file.read())
            image = images[0]  # First page
        else:
            image = Image.open(uploaded_file)

        st.image(image, caption="Uploaded Image", use_column_width=True)

        # OCR to extract text
        ocr_text = pytesseract.image_to_string(image)
        st.text_area("Raw OCR Output", ocr_text, height=150)

        # Extract MRZ lines (only letters, numbers, <, length 30-44)
        mrz_lines = [line for line in ocr_text.split("\n") if re.match(r'^[A-Z0-9<]{30,44}$', line)]
        
        if len(mrz_lines) >= 2:
            mrz_code = "\n".join(mrz_lines[-2:])  # Usually last 2 lines
            st.text_area("Detected MRZ", mrz_code, height=100)

            # Parse MRZ manually
            st.write("Parsed MRZ Data (basic fields):")
            if len(mrz_lines[-2]) == 44:  # TD3 passport
                line1 = mrz_lines[-2]
                line2 = mrz_lines[-1]

                st.write(f"**Document Type:** {line1[0]}")
                st.write(f"**Issuing Country:** {line1[2:5]}")
                names = line1[5:].split("<<")
                st.write(f"**Surname:** {names[0].replace('<',' ')}")
                st.write(f"**Given Names:** {names[1].replace('<',' ')}")
                st.write(f"**Passport Number:** {line2[0:9].replace('<','')}")
                st.write(f"**Nationality:** {line2[10:13]}")
                st.write(f"**Date of Birth:** {line2[13:19]}")
                st.write(f"**Sex:** {line2[20]}")
                st.write(f"**Expiration Date:** {line2[21:27]}")

        else:
            st.warning("Could not detect MRZ lines. Make sure the image is clear and MRZ is visible.")

    except Exception as e:
        st.error(f"Error processing file: {e}")

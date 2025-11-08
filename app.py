import streamlit as st
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
from mrz.reader import read_mrz
import io

st.set_page_config(page_title="Passport MRZ Reader", page_icon="✈️")
st.title("Passport MRZ Reader")

st.write("Upload an image or PDF of a passport, and get the MRZ data and Amadeus DOCS command.")

# File uploader
uploaded_file = st.file_uploader("Upload passport image or PDF", type=["png", "jpg", "jpeg", "pdf"])

if uploaded_file:
    file_type = uploaded_file.type
    text_from_file = ""

    if file_type == "application/pdf":
        # Convert PDF pages to images
        images = convert_from_bytes(uploaded_file.read())
        st.write(f"PDF converted to {len(images)} image(s)")
        for i, image in enumerate(images):
            st.image(image, caption=f"Page {i+1}")
            text_from_file += pytesseract.image_to_string(image)
    else:
        # Assume image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image")
        text_from_file = pytesseract.image_to_string(image)

    # Try to read MRZ
    mrz_data = read_mrz(text_from_file)
    if mrz_data.valid:
        st.success("MRZ successfully read!")
        st.json(mrz_data.to_dict())

        # Generate Amadeus DOCS command
        first_name = mrz_data.names.replace(" ", "/")
        last_name = mrz_data.surname.replace(" ", "/")
        doc_type = mrz_data.type
        doc_number = mrz_data.number
        nationality = mrz_data.nationality
        expiry = mrz_data.expiration_date.strftime("%y%m%d")  # YYMMDD format

        amadeus_command = f"DOCS/YY/{doc_type}/{doc_number}/{last_name}/{first_name}/{nationality}/{expiry}"
        st.code(amadeus_command, language="bash")
    else:
        st.error("Could not read MRZ. Please check the image quality.")

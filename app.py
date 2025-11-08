import streamlit as st
from PIL import Image
from pdf2image import convert_from_bytes
from mrz.reader import read_mrz
import pytesseract
import io

st.set_page_config(page_title="MRZ Reader", layout="centered")
st.title("MRZ Reader App")
st.write("Upload an image or PDF containing a machine-readable zone (MRZ).")

# File uploader
uploaded_file = st.file_uploader("Choose an image or PDF", type=["png", "jpg", "jpeg", "pdf"])

def process_image(image):
    """Process a PIL image and extract MRZ."""
    st.image(image, caption="Uploaded Image", use_column_width=True)
    text = pytesseract.image_to_string(image)
    mrz_result = read_mrz(text)
    if mrz_result.valid:
        st.success("MRZ found!")
        st.json(mrz_result.to_dict())
    else:
        st.warning("No valid MRZ detected. Try a clearer image.")

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        # Convert PDF pages to images
        pages = convert_from_bytes(uploaded_file.read())
        st.write(f"{len(pages)} page(s) detected in PDF.")
        for i, page in enumerate(pages):
            st.subheader(f"Page {i + 1}")
            process_image(page)
    else:
        # Process image file
        image = Image.open(uploaded_file)
        process_image(image)

import streamlit as st
from PIL import Image
from utils import pdf_to_image, extract_mrz, extract_text, generate_docs_code

st.title("Passport MRZ & DOCS Code Extractor")

uploaded_file = st.file_uploader("Upload a passport image or PDF", type=["png", "jpg", "jpeg", "pdf"])

if uploaded_file:
    # Convert PDF to Image if needed
    if uploaded_file.type == "application/pdf":
        image = pdf_to_image(uploaded_file)
    else:
        image = Image.open(uploaded_file)

    # Extract MRZ info
    mrz_data = extract_mrz(image)

    if mrz_data:
        st.subheader("MRZ Data")
        st.write(f"First Name: {mrz_data.get('names')}")
        st.write(f"Last Name: {mrz_data.get('surname')}")
        doc_number = mrz_data.get("number")
        docs_code = generate_docs_code(mrz_data.get('surname'), mrz_data.get('names'), doc_number)
        st.subheader("Generated Amadeus DOCS Code")
        st.write(docs_code)
    else:
        st.warning("MRZ not detected. Using OCR fallback...")
        text = extract_text(image)
        st.text_area("Extracted Text", text)

import streamlit as st
from PIL import Image
from utils import pdf_to_image, extract_mrz_text, parse_mrz_data, generate_docs_code

st.set_page_config(page_title="Passport MRZ & DOCS Extractor", layout="centered")
st.title("🛂 Passport MRZ & DOCS Code Extractor")

uploaded_file = st.file_uploader("Upload a passport image or PDF", type=["png", "jpg", "jpeg", "pdf"])

if uploaded_file:
    # Convert PDF to image if needed
    if uploaded_file.type == "application/pdf":
        image = pdf_to_image(uploaded_file.read())
    else:
        image = Image.open(uploaded_file)

    st.image(image, caption="Uploaded Passport Page", use_column_width=True)

    # Extract MRZ text
    mrz_text = extract_mrz_text(image)
    mrz_data = parse_mrz_data(mrz_text)

    if mrz_data:
        st.subheader("✅ MRZ Data Extracted")
        st.write(f"**First Name:** {mrz_data.get('first_name')}")
        st.write(f"**Last Name:** {mrz_data.get('last_name')}")
        st.write(f"**Document Number:** {mrz_data.get('document_number')}")

        docs_code = generate_docs_code(
            mrz_data.get('last_name'),
            mrz_data.get('first_name'),
            mrz_data.get("document_number")
        )
        st.subheader("📝 Generated Amadeus DOCS Code")
        st.code(docs_code)
    else:
        st.warning("⚠ MRZ not detected. Please ensure the bottom part of the passport is visible.")

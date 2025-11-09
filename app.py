import streamlit as st
from utils import pdf_to_image, extract_mrz_data, generate_docs_code

st.title("Passport MRZ Reader & Amadeus DOCS Generator")

uploaded_file = st.file_uploader("Upload Passport (Image or PDF)", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file:
    # Save uploaded file
    file_path = f"temp_{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    # Convert PDF → image if needed
    if uploaded_file.type == "application/pdf":
        st.info("Converting PDF to image...")
        image_path = pdf_to_image(file_path)
    else:
        image_path = file_path

    st.image(image_path, caption="Uploaded Passport", use_container_width=True)

    # Extract MRZ
    st.info("Extracting MRZ data...")
    data = extract_mrz_data(image_path)

    if data:
        st.success("✅ MRZ Detected and Parsed Successfully!")
        st.write(data)

        docs_code = generate_docs_code(data)
        st.text_area("Amadeus DOCS Line", docs_code, height=100)
    else:
        st.error("⚠ MRZ not detected. Please upload a clearer image showing both MRZ lines.")

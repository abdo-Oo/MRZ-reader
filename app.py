import streamlit as st
import numpy as np
from PIL import Image
from pdf2image import convert_from_path
from utils.mrz_extract import extract_mrz_from_image
from utils.docs_generator import generate_docs

st.title("Passport MRZ Extractor + Amadeus DOCS Generator")

uploaded = st.file_uploader("Upload Passport Image or PDF", type=["jpg", "png", "jpeg", "pdf"])

if uploaded:
    if uploaded.type == "application/pdf":
        images = convert_from_path(uploaded)
        image = np.array(images[0])
    else:
        image = np.array(Image.open(uploaded))

    st.image(image, caption="Uploaded File", use_column_width=True)

    st.write("🔍 Extracting MRZ...")
from utils.image_cleaner import normalize_image

clean_image = normalize_image(image)

mrz_data, rotated_img = extract_mrz_from_image(clean_image)

    if not mrz_data:
        st.error("❌ MRZ could not be detected. Try a clearer image.")
    else:
        st.success("✅ MRZ Detected")
        st.json(mrz_data)

        # Generate Amadeus command
        docs = generate_docs(mrz_data)

        st.subheader("✔️ Amadeus DOCS Command")
        st.code(docs)

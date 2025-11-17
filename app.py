import streamlit as st
import numpy as np
from PIL import Image
import fitz  # PyMuPDF

from utils.mrz_extract import extract_mrz_from_image
from utils.image_cleaner import normalize_image
from utils.docs_generator import generate_docs

st.title("Passport MRZ Extractor + Amadeus DOCS Generator")

uploaded = st.file_uploader(
    "Upload Passport Image or PDF",
    type=["jpg", "jpeg", "png", "pdf"]
)

if uploaded:
    # ---------------------------
    # LOAD IMAGE / PDF
    # ---------------------------
    if uploaded.type == "application/pdf":
        pdf = fitz.open(stream=uploaded.read(), filetype="pdf")
        page = pdf[0]
        pix = page.get_pixmap(dpi=200)
        image = np.frombuffer(
            pix.samples, dtype=np.uint8
        ).reshape(pix.height, pix.width, pix.n)
    else:
        image = np.array(Image.open(uploaded))

    st.subheader("📄 Uploaded File")
    st.image(image, use_column_width=True)

    # ---------------------------
    # CLEAN IMAGE
    # ---------------------------
    clean_image = normalize_image(image)

    # ---------------------------
    # MRZ Extraction
    # ---------------------------
    st.write("🔍 Extracting MRZ... please wait.")

    mrz_data, rotated_img = extract_mrz_from_image(clean_image)

    if not mrz_data:
        st.error("❌ Could not detect MRZ. Try a clearer or higher resolution image.")
    else:
        st.success("✅ MRZ Detected Successfully")

        st.subheader("MRZ Data:")
        st.json(mrz_data)

        # ---------------------------
        # Generate Amadeus DOCS
        # ---------------------------
        docs = generate_docs(mrz_data)

        st.subheader("📘 Amadeus DOCS Command")
        st.code(docs)

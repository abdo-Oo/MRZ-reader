import streamlit as st
from utils import extract_mrz_text, parse_mrz_data, generate_docs_code
from pdf2image import convert_from_bytes
from PIL import Image
import io

# ----- Streamlit page setup -----
st.set_page_config(
    page_title="Passport MRZ Reader",
    page_icon="🛂",
    layout="centered"
)

# ----- App header -----
st.markdown(
    """
    <h2 style="text-align:center; color:#004aad;">🛂 Passport MRZ Reader</h2>
    <p style="text-align:center; color:gray;">
        Upload a passport image or PDF — we’ll extract the MRZ details and generate an Amadeus DOCS command.
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

# ----- File uploader -----
uploaded_file = st.file_uploader(
    "Upload Passport Image or PDF",
    type=["jpg", "jpeg", "png", "pdf"]
)

if uploaded_file:
    try:
        # Convert PDF to image if needed
        if uploaded_file.type == "application/pdf":
            pages = convert_from_bytes(uploaded_file.read())
            passport_image = pages[0]
        else:
            passport_image = Image.open(uploaded_file)

        st.image(passport_image, caption="Uploaded Passport", use_container_width=True)

        # Extract MRZ text
        with st.spinner("Extracting MRZ data..."):
            mrz_text = extract_mrz_text(passport_image)

        if mrz_text:
            parsed_data = parse_mrz_data(mrz_text)
            if parsed_data:
                st.success("✅ MRZ successfully detected!")
                st.subheader("Extracted Passport Details")
                st.write(parsed_data)

                # Generate Amadeus DOCS code
                docs_code = generate_docs_code(parsed_data)
                st.subheader("Generated Amadeus DOCS Command")
                st.code(docs_code, language="text")
                st.info("You can copy this directly into Amadeus without modification.")
            else:
                st.warning("⚠ Unable to parse MRZ details. Please try a clearer image.")
        else:
            st.warning("⚠ MRZ not detected. Ensure the lower MRZ section is visible and clear.")

    except Exception as e:
        st.error(f"An error occurred while processing: {str(e)}")

else:
    st.info("👆 Please upload a passport image or PDF file to begin.")

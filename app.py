import streamlit as st
from utils import load_image, extract_mrz_data, parse_mrz, generate_srdocs

st.set_page_config(page_title="Passport MRZ to SRDOCS", page_icon="🛂", layout="centered")

st.title("🛂 Passport MRZ to SRDOCS Generator")
st.write("Upload a passport photo or PDF — the app will extract MRZ details and generate the SRDOCS command for Amadeus.")

uploaded = st.file_uploader("Upload passport image or PDF", type=["jpg", "jpeg", "png", "pdf"])

if uploaded:
    with st.spinner("Processing..."):
        image = load_image(uploaded)
        st.image(image, caption="Uploaded Passport", use_container_width=True)
        mrz = extract_mrz_data(image)
        if mrz:
            data = parse_mrz(mrz)
            st.success("✅ MRZ successfully detected!")
            st.write(data)

            srdocs = generate_srdocs(data)
            st.subheader("✈️ Amadeus SRDOCS Command")
            st.code(srdocs, language="text")
            st.info("Copy and paste this directly into Amadeus.")
        else:
            st.warning("⚠ MRZ not detected. Try a clearer or more complete image.")
else:
    st.info("👆 Please upload a passport image or PDF to begin.")

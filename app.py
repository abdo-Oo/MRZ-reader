import streamlit as st
from passporteye import read_mrz

st.title("Passport MRZ Name Extractor")

uploaded_file = st.file_uploader("Upload a passport image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    with open("temp.jpg", "wb") as f:
        f.write(uploaded_file.getbuffer())

    mrz = read_mrz("temp.jpg")

    if mrz:
        data = mrz.to_dict()
        surname = data.get('surname', '').strip()
        given_names = data.get('names', '').strip()

        st.success("✅ Name extracted successfully!")
        st.write(f"**Last Name:** {surname}")
        st.write(f"**First Name(s):** {given_names}")
    else:
        st.error("❌ Could not read MRZ. Try a clearer image.")

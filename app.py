import streamlit as st
from passporteye import read_mrz
from datetime import datetime

st.title("Passport MRZ → Amadeus DOCS Generator")

uploaded_file = st.file_uploader("Upload a passport image", type=["jpg", "jpeg", "png"])

def format_date(date_str):
    """Convert YYMMDD to DDMMMYY (Amadeus style)."""
    try:
        return datetime.strptime(date_str, "%y%m%d").strftime("%d%b%y").upper()
    except Exception:
        return ""

if uploaded_file:
    with open("temp.jpg", "wb") as f:
        f.write(uploaded_file.getbuffer())

    mrz = read_mrz("temp.jpg")

    if mrz:
        data = mrz.to_dict()

        surname = data.get('surname', '').strip()
        given_names = data.get('names', '').strip()
        nationality = data.get('nationality', '').strip()
        passport_number = data.get('number', '').strip()
        dob = data.get('date_of_birth', '').strip()
        sex = data.get('sex', '').strip()
        expiry = data.get('expiration_date', '').strip()
        issuing_country = data.get('country', '').strip()

        st.success("✅ MRZ data extracted successfully!")

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Surname:**", surname)
            st.write("**Given Names:**", given_names)
            st.write("**Gender:**", sex)
            st.write("**Date of Birth:**", format_date(dob))
        with col2:
            st.write("**Nationality:**", nationality)
            st.write("**Passport #:**", passport_number)
            st.write("**Expiry:**", format_date(expiry))
            st.write("**Issuing Country:**", issuing_country)

        st.divider()

        airline_code = st.text_input("Enter Airline Code (e.g. TK, EK, QR):").upper().strip()
        if airline_code:
            docs_command = (
                f"SR DOCS YY HK1 P/{nationality}/{passport_number}/"
                f"{issuing_country}/{format_date(dob)}/{sex}/"
                f"{format_date(expiry)}/{surname}/{given_names.replace(' ', '')}"
            )
            st.text_area("Amadeus DOCS Command:", docs_command, height=80)
            st.caption("Copy and paste this directly into Amadeus PNR.")
    else:
        st.error("❌ Could not read MRZ. Try a clearer passport image.")

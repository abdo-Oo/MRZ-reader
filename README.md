# Passport MRZ Extractor + Amadeus DOCS Generator

A Streamlit application that:

- Accepts PDF or image uploads of passport bio pages
- Auto-rotates to detect the MRZ
- Extracts MRZ fields (name, DOB, passport number, nationality, expiration, etc.)
- Generates the Amadeus DOCS command automatically
- Works on Streamlit Cloud (no OpenCV / Poppler required)

## Features
✔ Accept JPG/PNG/PDF  
✔ Robust MRZ detection (0°, 90°, 180°, 270°)  
✔ Extract surname + given names  
✔ Generate airline DOCS format  
✔ No system dependencies  

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py

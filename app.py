import streamlit as st
from utils import pdf_to_image, extract_mrz_data, generate_docs_code

# ======================
# Page Setup
# ======================
st.set_page_config(
    page_title="Passport MRZ Reader",
    page_icon="",
    layout="centered",
)

# ======================
# Logo and Header
# ======================
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo.png", use_container_width=True)

st.markdown(
    "<h1 style='text-align:center; color:#003366;'>Passport MRZ Reader & Amadeus DOCS Generator</h1>",
    unsafe_allow_html=True,
)

# ======================
# Custom Styling
# ======================
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: url("https://images.unsplash.com/photo-1502920917128-1aa500764b43");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    [data-testid="stAppViewContainer"] > div {
        background-color: rgba(255, 255, 255, 0.88);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    div.stButton > button {
        background-color: #004080;
        color: white;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
    }
    div.stButton > button:hover {
        background-color: #0055aa;
        color: #f0f0f0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ======================
# File Upload Section
# ======================
st.markdown("### 📄 Upload Passport (Image or PDF)")
uploaded_file = st.file_uploader("Choose file", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file:
    file_path = f"temp_{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    if uploaded_file.type == "application/pdf":
        st.info("Converting PDF to image...")
        image_path = pdf_to_image(file_path)
    else:
        image_path = file_path

    st.image(image_path, caption="Uploaded Passport", use_container_width=True)

    with st.spinner("🔍 Extracting MRZ data..."):
        data = extract_mrz_data(image_path)

    if data:
        st.success("✅ MRZ Detected Successfully!")
        with st.expander("View Extracted Passport Data"):
            st.json(data)

        docs_code = generate_docs_code(data)

        st.markdown("### ✈️ Copy & Paste into Amadeus:")
        st.text_area("", docs_code, height=100)
        st.caption("This DOCS command is fully formatted for Amadeus — no edits required.")

    else:
        st.error("⚠ MRZ not detected. Please upload a clearer image showing both MRZ lines.")

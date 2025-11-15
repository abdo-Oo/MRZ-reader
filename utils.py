import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import numpy as np
import re


def load_image(file):
    """
    Detect if PDF or image and return a Pillow image (RGB)
    """
    if file.filename.lower().endswith(".pdf"):
        # Convert last page of PDF to image
        pages = convert_from_path(file.file, fmt="png")
        img = pages[-1]  # MRZ usually on last page
        return img.convert("RGB")

    else:
        img = Image.open(file.file)
        return img.convert("RGB")


def extract_mrz_from_image(img: Image.Image):
    """
    Extract MRZ from image using Tesseract only (no OpenCV required)
    """

    # Convert image to grayscale to improve OCR
    gray = img.convert("L")

    # Tesseract configuration optimized for MRZ
    config = (
        "--oem 1 --psm 6 "
        "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<"
    )

    text = pytesseract.image_to_string(gray, config=config)

    # Clean text and split into lines
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # MRZ lines must be:
    # - contain "<"
    # - length >= 30 characters
    mrz_lines = [l for l in lines if "<" in l and len(l) >= 30]

    if len(mrz_lines) < 2:
        raise ValueError("MRZ could not be detected from the image.")

    # Return only the first two valid MRZ lines
    return mrz_lines[0] + "\n" + mrz_lines[1]

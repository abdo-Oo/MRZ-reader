from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

from utils import load_image, extract_mrz_from_image
from mrz_parser import parse_mrz
from docs_generator import generate_docs_line

app = FastAPI()


@app.post("/upload-passport")
async def upload_passport(file: UploadFile = File(...)):
    try:
        # Load passport image or PDF converted to image
        img = load_image(file)

        # Extract MRZ using OCR
        mrz = extract_mrz_from_image(img)

        # Parse MRZ fields
        data = parse_mrz(mrz)

        # Generate DOCS YY line
        docs_line = generate_docs_line(data)

        return JSONResponse({
            "mrz_raw": mrz,
            "parsed_data": data,
            "docs_line": docs_line
        })

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

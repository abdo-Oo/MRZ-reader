from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from utils import load_image, extract_mrz_from_image
from mrz_parser import parse_mrz
from docs_generator import generate_docs_line

import hashlib

app = FastAPI()

# Add session middleware (for login cookies)
app.add_middleware(SessionMiddleware, secret_key="SUPER_SECRET_KEY_CHANGE_THIS")

# Static + template folders
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# ---- LOGIN CREDENTIALS (change them) ----
USERNAME = "teamuser"
PASSWORD_HASH = hashlib.sha256("mypassword123".encode()).hexdigest()
# -----------------------------------------


def is_logged_in(request: Request):
    return request.session.get("logged_in") is True


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if not is_logged_in(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):

    password_hash = hashlib.sha256(password.encode()).hexdigest()

    if username == USERNAME and password_hash == PASSWORD_HASH:
        request.session["logged_in"] = True
        return RedirectResponse("/", status_code=302)

    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid login"})


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login")


@app.post("/process", response_class=HTMLResponse)
async def process(request: Request, file: UploadFile = File(...)):

    if not is_logged_in(request):
        return RedirectResponse("/login")

    try:
        img = load_image(file)
        mrz_raw = extract_mrz_from_image(img)
        parsed = parse_mrz(mrz_raw)
        docs_line = generate_docs_line(parsed)

        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "mrz_raw": mrz_raw,
                "parsed_data": parsed,
                "docs_line": docs_line
            }
        )

    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": str(e)}
        )

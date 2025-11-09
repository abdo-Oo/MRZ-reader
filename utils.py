from datetime import datetime

def format_date(date_str):
    """Convert YYYY-MM-DD or YYMMDD or similar to DDMMMYY."""
    if not date_str:
        return ""
    try:
        # Try common formats from MRZ
        for fmt in ("%y%m%d", "%Y-%m-%d", "%d%m%y", "%Y%m%d"):
            try:
                d = datetime.strptime(date_str, fmt)
                return d.strftime("%d%b%y").upper()
            except ValueError:
                continue
    except Exception:
        pass
    return date_str  # fallback (keep original if unknown)


def generate_docs_code(data):
    """Generate a valid Amadeus DOCS command (copy-paste ready)."""
    if not data:
        return None

    nationality = data.get("nationality", "").upper()
    last_name = data.get("last_name", "").upper().replace(" ", "")
    first_name = data.get("first_name", "").upper().replace(" ", "")
    gender = data.get("gender", "U").upper()[0]  # Default 'U' if unknown
    dob = format_date(data.get("birth_date", ""))
    expiry = format_date(data.get("expiry_date", ""))
    passport = data.get("passport_number", "").upper().replace(" ", "")

    # Construct DOCS command
    docs = (
        f"DOCS YY HK1 P/{nationality}/{passport}/{nationality}/{expiry}/"
        f"{gender}/{dob}/{last_name}/{first_name}"
    )
    return docs

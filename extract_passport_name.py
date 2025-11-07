import cv2
import pytesseract
from passporteye import read_mrz

def extract_name_from_passport(image_path):
    """
    Extracts first and last name from passport MRZ.
    Returns (surname, given_names) or (None, None) if not found.
    """
    print(f"Processing: {image_path}")
    
    # Try with PassportEye (more reliable)
    mrz = read_mrz(image_path)
    if mrz:
        data = mrz.to_dict()
        surname = data.get('surname', '').strip()
        given_names = data.get('names', '').strip()
        return surname, given_names
    
    # Fallback to OCR manually if PassportEye fails
    print("PassportEye failed, trying OCR fallback...")
    
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError("Image not found.")
    
    h = img.shape[0]
    mrz_area = img[int(h*0.75):, :]  # bottom quarter
    gray = cv2.cvtColor(mrz_area, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    config = '--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ<0123456789'
    text = pytesseract.image_to_string(th, config=config)
    
    lines = [l.strip().replace(' ', '') for l in text.splitlines() if len(l.strip()) >= 30]
    if not lines:
        return None, None
    
    mrz_line = lines[-1]  # usually second line has name
    name_field = mrz_line[5:] if len(mrz_line) > 5 else mrz_line
    
    if '<<' in name_field:
        surname, given_part = name_field.split('<<', 1)
    else:
        return None, None
    
    surname = surname.replace('<', ' ').strip()
    given_names = ' '.join([p for p in given_part.split('<') if p]).strip()
    
    return surname, given_names


if __name__ == "__main__":
    image_path = input("Enter passport image path: ").strip()
    surname, given_names = extract_name_from_passport(image_path)
    
    if surname and given_names:
        print(f"\n✅ Extracted Successfully:")
        print(f"Last Name: {surname}")
        print(f"First Name(s): {given_names}")
    else:
        print("❌ Could not extract name from the image.")

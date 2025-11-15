from mrz.base import MRZ

def parse_mrz(mrz_text):
    """
    Input: Full MRZ text (2 lines)
    Output: dict with parsed values
    """
    mrz = MRZ(mrz_text, check=False)
    
    surname = mrz.surname
    given_names = " ".join(mrz.names)

    return {
        "surname": surname,
        "given_names": given_names,
        "passport_number": mrz.number,
        "nationality": mrz.nationality,
        "dob": mrz.date_of_birth,
        "expiry": mrz.expiration_date,
        "gender": mrz.sex
    }

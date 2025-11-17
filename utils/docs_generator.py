from dateutil.parser import parse

def format_amadeus_date(date_str):
    d = parse(date_str)
    return d.strftime("%d%b%y").upper()

def generate_docs(mrz_data, pax_number=1):
    return (
        f"SRDOCS-P{pax_number}/P/"
        f"{mrz_data['nationality']}/"
        f"{mrz_data['passport_number']}/"
        f"{mrz_data['country']}/"
        f"{format_amadeus_date(mrz_data['date_of_birth'])}/"
        f"{mrz_data['sex']}/"
        f"{format_amadeus_date(mrz_data['expiration_date'])}/"
        f"{mrz_data['surname']}/"
        f"{mrz_data['given_names'].replace(' ', '-')}"
    )

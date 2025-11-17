from dateutil.parser import parse

def format_amadeus_date(date_str):
    d = parse(date_str)
    return d.strftime("%d%b%y").upper()

def generate_docs(mrz):
    """
    Build Amadeus DOCS command.
    """
    return (
        f"SRDOCS-P1/P/"
        f"{mrz['nationality']}/"
        f"{mrz['passport_number']}/"
        f"{mrz['country']}/"
        f"{format_amadeus_date(mrz['date_of_birth'])}/"
        f"{mrz['sex']}/"
        f"{format_amadeus_date(mrz['expiration_date'])}/"
        f"{mrz['surname']}/"
        f"{mrz['given_names'].replace(' ', '-')}"
    )

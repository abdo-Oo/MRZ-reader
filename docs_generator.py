MONTHS = ["JAN","FEB","MAR","APR","MAY","JUN",
          "JUL","AUG","SEP","OCT","NOV","DEC"]

def convert_mrz_date(mrz_date):
    yy = int(mrz_date[0:2])
    mm = int(mrz_date[2:4])
    dd = mrz_date[4:6]

    year = 1900 + yy if yy > 30 else 2000 + yy
    month = MONTHS[mm - 1]

    return f"{dd}{month}{str(year)[2:]}"


def generate_docs_line(data):
    """
    Input: dict from parse_mrz()
    """
    surname = data["surname"]
    given = data["given_names"]
    passport = data["passport_number"]
    nationality = data["nationality"]
    dob = convert_mrz_date(data["dob"])
    expiry = convert_mrz_date(data["expiry"])
    gender = data["gender"]

    return (
        f"SR DOCS YY HK1-P/{nationality}/{passport}/{nationality}/"
        f"{dob}/{gender}/{expiry}/{surname}/{given}"
    )

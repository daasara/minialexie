from datetime import date, datetime

def parse_from_date(request):
    if "from" in request.GET:
        try:
            from_date = datetime.strptime(request.GET['from'], "%Y-%m-%d").date()
        except ValueError:
            from_date = date(1900, 1, 1)
    else:
        from_date = date(1900, 1, 1)

    return from_date

def parse_to_date(request):
    if "to" in request.GET:
        try:
            to_date = datetime.strptime(request.GET['to'], "%Y-%m-%d").date()
        except ValueError:
            to_date = date(2100, 1, 1)
    else:
        to_date = date(2100, 1, 1)

    return to_date

def parse_amount(s):
    """Convert an amount string s to an integer representing the number of cents in s"""
    return round(float(s.replace(",", "."))*100)

def display_amount(n):
    """Convert amount n in cents (an integer) to an amount with decimal mark (1,50)"""
    s = str(n)
    return s[:-2] + "," + s[-2:]

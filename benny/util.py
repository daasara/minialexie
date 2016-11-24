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

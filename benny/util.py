from datetime import date, datetime

from django.db.models import Max

DEFAULT_FROM_DATE = date(2001, 1, 1)
DEFAULT_TO_DATE = date(2029, 1, 1)

def parseDate(s, defaultDate=DEFAULT_FROM_DATE):
    """Parse a string s in the formats 15/01/16 or 15/01/2016"""
    try:
        # 2-digit year
        parsedDate = datetime.strptime(s, "%d/%m/%y")
    except ValueError:
        try:
            # 4-digit year
            parsedDate = datetime.strptime(s, "%d/%m/%Y")
        except ValueError:  # some other invalid format
            parsedDate = defaultDate
    except KeyError:
        parsedDate = defaultDate
    return parsedDate
    
def parseFromDate(request):
    try:
        parsedDate = parseDate(request.session['fromDate'], DEFAULT_FROM_DATE)
    except KeyError:
        parsedDate = DEFAULT_FROM_DATE
    request.session['fromDate'] = displayDate(parsedDate)
    return parsedDate

def parseToDate(request):
    try:
        parsedDate = parseDate(request.session['toDate'], DEFAULT_TO_DATE)
    except KeyError:
        parsedDate = DEFAULT_TO_DATE
    request.session['toDate'] = displayDate(parsedDate)
    return parsedDate

def displayDate(d):
    return d.strftime("%d/%m/%y")

def parseAccountTypeSign(value):
    # Given a form's value, return +/-1
    if value == 0:
        return 1
    else:
        return round(value / abs(value))

def nextOrderIndex(model, user):
    objects = model.objects.filter(user=user)
    if not objects:
        return 1
    else:
        return objects.aggregate(Max('order'))['order__max'] + 1

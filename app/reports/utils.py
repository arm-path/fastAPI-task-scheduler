from datetime import date
from datetime import timedelta


def get_date_month(date_from: date = None):
    if not date_from:
        date_from = date.today()
    date_from = date_from.replace(day=1)
    if date_from.month == 12:
        date_to = date_from.replace(year=date_from.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        date_to = date_from.replace(month=date_from.month + 1, day=1) - timedelta(days=1)
    return date_from, date_to

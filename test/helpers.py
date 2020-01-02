from datetime import datetime


def format_day(dayofyear):
    """Turn day of year to 'January 02' type string
    Needed to test during leap years
    """
    year = datetime.now().year
    day = datetime.strptime(f'{year} {dayofyear}', '%Y %j')
    return day.strftime('%B %d')

import math
from decimal import Decimal


def decimal_hours_to_time(decimal_hours: Decimal) -> str:
    """
    Converts a Decimal to HH:MM representation
    """
    hours = math.floor(decimal_hours)
    decimal_minutes = decimal_hours % 1 * 60
    minutes = round(decimal_minutes)
    if minutes == 60:
        hours += 1
        minutes = 0
    return f"{hours:02}:{minutes:02}"

import decimal

CENTI = decimal.Decimal('0.01')
DECIMAL_CONTEXT = decimal.DefaultContext.copy()
DECIMAL_CONTEXT.rounding = decimal.ROUND_HALF_UP


def round_to_centi(d):
    return DECIMAL_CONTEXT.quantize(d, CENTI)

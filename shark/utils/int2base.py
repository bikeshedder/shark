# Credits:
# http://stackoverflow.com/questions/2267362/convert-integer-to-a-string-in-a-given-numeric-base-in-python

import string
digs = string.digits + string.ascii_lowercase

def int2base(x, base):
    if x < 0:
        sign = -1
    elif x == 0:
        return digs[0]
    else:
        sign = 1

    x *= sign
    digits = []

    while x:
        digits.append(digs[int(x % base)])
        x = int(x / base)

    if sign < 0:
        digits.append('-')

    digits.reverse()

    return ''.join(digits)

# Credits:
# http://stackoverflow.com/questions/2267362/convert-integer-to-a-string-in-a-given-numeric-base-in-python

import string
digs = string.digits + string.lowercase

def int2base(x, base):
    if x < 0: sign = -1
    elif x==0: return '0'
    else: sign = 1
    x *= sign
    digits = []
    while x:
        digits.append(digs[x % base])
        x /= base
    if sign < 0:
        digits.append('-')
    digits.reverse()
    return ''.join(digits)

def anonymize_iban(s):
    offset = (len(s) + 1) // 2
    return (offset * u'*') + s[offset:]

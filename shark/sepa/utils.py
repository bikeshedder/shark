def anonymize_iban(s):
    offset = (len(s) + 1) // 2
    return (offset * "*") + s[offset:]


# Temporary until SEPA app gets redone in order to remove this from settings.py
DEFAULT_SEPA = {
    "CREDITOR_ID": "",
    "CREDITOR_NAME": "",
    "CREDITOR_COUNTRY": "DE",
    "CREDITOR_IBAN": "",
    "CREDITOR_BIC": "",
    "DEFAULT_MANDATE_TYPE": "CORE",
    "TRANSACTION_REFERENCE_PREFIX": "",
    "PRE_NOTIFICATION_EMAIL_FROM": "",
    "PRE_NOTIFICATION_EMAIL_BCC": [],
}

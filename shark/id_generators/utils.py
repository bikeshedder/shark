from django.db import models


class CustomerNumberGenerators(models.TextChoices):
    INITIAL_AS_NUMBER = "INITNUM", "Initial as number Generator"


class InvoiceNumberGenerators(models.TextChoices):
    YEAR_CUSTOMER_N = "YEARCUSTN", "Year - Customer - N"
    CUSTOMER_YEAR_N = "CUSTYEARN", "Customer - Year - N"


def get_customer_generator(type: str):
    match type:
        case CustomerNumberGenerators.INITIAL_AS_NUMBER:
            return "shark.id_generators.self_referential.InitialAsNumber"
        case _:
            return "shark.id_generators.self_referential.InitialAsNumber"


def get_invoice_generator(type: str):
    match type:
        case InvoiceNumberGenerators.YEAR_CUSTOMER_N:
            return "shark.id_generators.relation_based.YearCustomerN"
        case InvoiceNumberGenerators.CUSTOMER_YEAR_N:
            return "shark.id_generators.relation_based.CustomerYearN"
        case _:
            return "shark.id_generators.relation_based.CustomerYearN"

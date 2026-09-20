RATES = {"USD": 87, "EUR": 100, "RUB": 1}
DEFAULT_CODE = "USD"


def normalize(code):
    code = (code or "").upper()
    if code in RATES:
        return code
    return DEFAULT_CODE


def rate_case(code_column):
    conditions = " ".join("WHEN '" + code + "' THEN " + str(rate) for code, rate in RATES.items())
    return "CASE " + code_column + " " + conditions + " ELSE 1 END"


def in_rubles(amount_column, code_column):
    return "(" + amount_column + " * " + rate_case(code_column) + ")"


def convert(amount_in_rubles, code):
    return round(float(amount_in_rubles) / RATES[code], 2)

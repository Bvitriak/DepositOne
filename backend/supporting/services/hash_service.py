import hashlib


def hash_value(value):
    return {"request": value, "result": hashlib.sha256(value.encode()).hexdigest()}

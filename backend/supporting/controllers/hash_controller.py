from flask import jsonify

from services import hash_service


def get_hash(value):
    return jsonify(hash_service.hash_value(value))

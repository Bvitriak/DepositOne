from flask import jsonify

from services import api_service


def list_apis():
    return jsonify(api_service.get_apis())

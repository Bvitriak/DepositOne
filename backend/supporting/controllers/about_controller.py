from flask import jsonify

from services import about_service


def get_about():
    return jsonify(about_service.get_about())

from flask import jsonify, g

from services import profile_service


def get_profile(connection):
    result, status = profile_service.get_profile(connection, g.user["id"])
    return jsonify(result), status


def release_token(connection):
    result, status = profile_service.release_token(connection, g.user["id"])
    return jsonify(result), status

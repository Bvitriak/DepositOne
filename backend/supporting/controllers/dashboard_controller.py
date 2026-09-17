from flask import jsonify

from services import dashboard_service


def overview(connection):
    return jsonify(dashboard_service.get_overview(connection))

from flask import jsonify

from services import notification_service


def list_notifications(connection):
    return jsonify(notification_service.get_notifications(connection))

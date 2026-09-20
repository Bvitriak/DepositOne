from flask import Blueprint

from controllers import report_controller
from utils.auth import token_required
from utils.db import with_db

report_routes = Blueprint("report", __name__)
report_routes.add_url_rule("/api/reports", view_func=token_required(with_db(report_controller.list_reports)), methods=["GET"])
report_routes.add_url_rule("/api/reports/cash-flow", view_func=token_required(with_db(report_controller.get_cash_flow)), methods=["GET"])

from flask import request, jsonify

from services import report_service
from utils import currency
from utils.params import read_list_params


def list_reports(connection):
    search, sort, order, page, page_size = read_list_params(request.args, "amount", "desc")
    code = currency.normalize(request.args.get("currency"))
    result, status = report_service.list_reports(connection, search, sort, order, page, page_size, code)
    return jsonify(result), status


def get_cash_flow(connection):
    result, status = report_service.get_cash_flow(connection, currency.normalize(request.args.get("currency")))
    return jsonify(result), status

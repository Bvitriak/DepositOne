from repositories import portfolio_repository
from utils import currency


def get_portfolio(connection, code):
    portfolio = portfolio_repository.get_portfolio(connection)
    return {
        "portfolio": {
            "depositors": portfolio.depositors,
            "active_deposits": portfolio.active_deposits,
            "total_amount": currency.convert(portfolio.total_amount, code),
        },
        "operations": {
            "signed_contracts": portfolio.signed_contracts,
            "pending_contracts": portfolio.pending_contracts,
            "rejected_contracts": portfolio.rejected_contracts,
        },
    }, 200

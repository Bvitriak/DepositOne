from core_service.app.routes.routes_analytics import register_analytics_routes
from core_service.app.routes.routes_contracts import register_contract_routes
from core_service.app.routes.routes_depositors import register_depositor_routes
from core_service.app.routes.routes_deposits import register_deposit_routes
from core_service.app.routes.routes_public import register_public_routes

def register_routes(app):
    register_public_routes(app)
    register_depositor_routes(app)
    register_deposit_routes(app)
    register_contract_routes(app)
    register_analytics_routes(app)

from fastapi import FastAPI
from supporting_service.schemas import ServiceEnvelope, AuthLoginRequest, NotificationRequest
from supporting_service.services.report_service import ( get_today_cash_flow, get_month_cash_flow, get_year_cash_flow, get_reports_snapshot )
from supporting_service.services.analytics_service import ( get_returns_tomorrow, get_dashboard_metrics, get_analytics_snapshot, get_deposits_list, get_dashboard_data )
from supporting_service.services.auth_service import login_user
from supporting_service.services.notification_service import send_notification

app = FastAPI(title="DepositOne Supporting Service",version="1.0.0",description="Supporting JSON service for reports, analytics, auth and notifications")

@app.get("/api/health", response_model=ServiceEnvelope)
def health():
    return {
        "ok": True,
        "service": "supporting",
        "module": "health",
        "data": {"status": "ok"},
        "message": "Сервис работает.",
        "error_type": None,
        "fallback_used": False,
    }

@app.get("/api/reports/today", response_model=ServiceEnvelope)
def reports_today():
    return get_today_cash_flow()

@app.get("/api/reports/month/{year}/{month}", response_model=ServiceEnvelope)
def reports_month(year: int, month: int):
    return get_month_cash_flow(year, month)

@app.get("/api/reports/year/{year}", response_model=ServiceEnvelope)
def reports_year(year: int):
    return get_year_cash_flow(year)

@app.get("/api/reports/summary", response_model=ServiceEnvelope)
def reports_summary():
    return get_reports_snapshot()

@app.get("/api/analytics/returns-tomorrow", response_model=ServiceEnvelope)
def analytics_returns_tomorrow():
    return get_returns_tomorrow()

@app.get("/api/analytics/metrics", response_model=ServiceEnvelope)
def analytics_metrics():
    return get_dashboard_metrics()

@app.get("/api/analytics/summary", response_model=ServiceEnvelope)
def analytics_summary():
    return get_analytics_snapshot()

@app.get("/api/analytics/dashboard", response_model=ServiceEnvelope)
def analytics_dashboard():
    return get_dashboard_data()

@app.get("/api/analytics/deposits", response_model=ServiceEnvelope)
def analytics_deposits(
    search: str | None = None,
    status: str | None = None,
    currency: str | None = None,
    min_amount: float | None = None,
    max_amount: float | None = None,
    sort_by: str = "id",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 20,
):
    return get_deposits_list(
        search=search,
        status=status,
        currency=currency,
        min_amount=min_amount,
        max_amount=max_amount,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )

@app.post("/api/auth/login", response_model=ServiceEnvelope)
def auth_login(payload: AuthLoginRequest):
    return login_user(payload)

@app.post("/api/notifications/send", response_model=ServiceEnvelope)
def notify(payload: NotificationRequest):
    return send_notification(payload)

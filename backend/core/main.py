from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from routes.depositor_routes import router as depositor_router
from routes.country_routes import router as country_router
from routes.deposit_routes import router as deposit_router
from routes.currency_routes import router as currency_router

application = FastAPI()
application.include_router(depositor_router)
application.include_router(country_router)
application.include_router(deposit_router)
application.include_router(currency_router)


@application.exception_handler(Exception)
async def internal_error(request: Request, error):
    return JSONResponse({"error": "internal server error", "fallback": True}, status_code=500)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(application, host="0.0.0.0", port=8002)

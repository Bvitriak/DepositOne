from __future__ import annotations
import logging
from typing import Any
from supporting_service.constants import (DEFAULT_TOKEN_TYPE, EMPTY_ROLES, MODULE_AUTH, SERVICE_NAME )
from supporting_service.utils.fallbacks import business_error, exception_fallback

logger = logging.getLogger(__name__)

def login_user(payload: Any) -> dict[str, Any]:
    try:
        username = getattr(payload, "username", "") or ""
        username = username.strip()
        password = getattr(payload, "password", "") or ""

        if not username or not password:
            logger.warning(
                "Auth failed: missing username or password, username=%r",
                username,
            )
            return business_error(
                SERVICE_NAME,
                MODULE_AUTH,
                "Логин и пароль обязательны.",
                data={
                    "access_token": None,
                    "token_type": DEFAULT_TOKEN_TYPE,
                    "username": username or None,
                    "roles": list(EMPTY_ROLES),
                },
            )

        logger.warning("Auth failed: invalid credentials for username=%r", username)
        return business_error(
            SERVICE_NAME,
            MODULE_AUTH,
            "Неверный логин или пароль.",
            data={
                "access_token": None,
                "token_type": DEFAULT_TOKEN_TYPE,
                "username": username,
                "roles": list(EMPTY_ROLES),
            },
        )
    except Exception as exc:
        logger.exception("Auth error while processing login request")
        return exception_fallback(
            SERVICE_NAME,
            MODULE_AUTH,
            exc,
            fallback_data={
                "access_token": None,
                "token_type": DEFAULT_TOKEN_TYPE,
                "username": None,
                "roles": list(EMPTY_ROLES),
            },
            default_message="Ошибка авторизации.",
        )

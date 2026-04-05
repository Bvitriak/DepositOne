from __future__ import annotations
from typing import Any, TypedDict

class ServiceResult(TypedDict):
    ok: bool
    data: Any
    message: str
    error_type: str | None
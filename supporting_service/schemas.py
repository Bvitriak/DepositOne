from typing import Any, Optional, Literal
from pydantic import BaseModel, Field

class ServiceEnvelope(BaseModel):
    ok: bool
    service: str
    module: str
    data: Any = None
    message: str = ""
    error_type: Optional[str] = None
    fallback_used: bool = False

class AuthLoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)

class NotificationRequest(BaseModel):
    channel: Literal["email", "sms", "push", "system"] = "system"
    recipient: str = Field(min_length=1)
    subject: str = ""
    message: str = Field(min_length=1)

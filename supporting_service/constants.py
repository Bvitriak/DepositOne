from decimal import Decimal
from enum import StrEnum

class OperationType(StrEnum):
    DEPOSIT_OPEN = "deposit_open"
    DEPOSIT_TOPUP = "deposit_topup"
    DEPOSIT_RETURN = "deposit_return"
    INTEREST_PAYMENT = "interest_payment"

INCOME_OPERATION_TYPES = (
    OperationType.DEPOSIT_OPEN.value,
    OperationType.DEPOSIT_TOPUP.value,
)

EXPENSE_OPERATION_TYPES = (
    OperationType.DEPOSIT_RETURN.value,
    OperationType.INTEREST_PAYMENT.value,
)

SERVICE_NAME = "supporting"

MODULE_REPORTS = "reports"
MODULE_AUTH = "auth"
MODULE_NOTIFICATIONS = "notifications"
MODULE_ANALYTICS = "analytics"
MODULE_HEALTH = "health"

TWO_PLACES = Decimal("0.01")
DEFAULT_DATABASE = "database/depositBank.db"
DEFAULT_NOTIFICATION_CHANNEL = "system"
DEFAULT_TOKEN_TYPE = "bearer"
EMPTY_ROLES: tuple[str, ...] = ()

from decimal import Decimal
from enum import StrEnum

class DepositStatus(StrEnum):
    ACTIVE = "active"
    CLOSED = "closed"
    BLOCKED = "blocked"

class CurrencyCode(StrEnum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"

class OperationType(StrEnum):
    DEPOSIT_OPEN = "deposit_open"
    DEPOSIT_TOPUP = "deposit_topup"
    DEPOSIT_RETURN = "deposit_return"
    INTEREST_PAYMENT = "interest_payment"

DEPOSIT_STATUSES = tuple(item.value for item in DepositStatus)
CURRENCIES = tuple(item.value for item in CurrencyCode)

INCOME_OPERATION_TYPES = (OperationType.DEPOSIT_OPEN.value, OperationType.DEPOSIT_TOPUP.value )

EXPENSE_OPERATION_TYPES = (OperationType.DEPOSIT_RETURN.value, OperationType.INTEREST_PAYMENT.value )

TWOPLACES = Decimal("0.01")
DAYS_IN_YEAR = Decimal("365")

DEFAULT_MASTER_DB = "database/depositBank.db"
DEFAULT_SLAVE_DB = "database/depositBankSlave.db"

MIN_PASSWORD_LENGTH = 8
REMEMBER_CHECKBOX_VALUE = "on"

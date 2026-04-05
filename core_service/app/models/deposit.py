from __future__ import annotations
from core_service.app.constants import CurrencyCode, DepositStatus
from core_service.app.models.base import BaseModel

class DepositModel(BaseModel):
    table_name = "deposits"

    def create_deposit(
        self,
        depositor_id: int,
        opened_by_user_id: int,
        deposit_type: str,
        amount: float,
        interest_rate: float,
        start_date: str,
        end_date: str,
        currency: str = CurrencyCode.RUB.value,
        capitalization: int = 0,
        auto_renewal: int = 0,
        status: str = DepositStatus.ACTIVE.value,
    ):
        sql = """
        INSERT INTO deposits (
            depositor_id,
            opened_by_user_id,
            deposit_type,
            amount,
            interest_rate,
            currency,
            start_date,
            end_date,
            status,
            capitalization,
            auto_renewal
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute(
            sql,
            (
                depositor_id,
                opened_by_user_id,
                deposit_type,
                amount,
                interest_rate,
                currency,
                start_date,
                end_date,
                status,
                capitalization,
                auto_renewal,
            ),
        )

    def update_deposit(
        self,
        deposit_id: int,
        depositor_id: int,
        deposit_type: str,
        amount: float,
        interest_rate: float,
        start_date: str,
        end_date: str,
        currency: str,
        capitalization: int,
        auto_renewal: int,
        status: str,
    ):
        sql = """
        UPDATE deposits
        SET
            depositor_id = ?,
            deposit_type = ?,
            amount = ?,
            interest_rate = ?,
            start_date = ?,
            end_date = ?,
            status = ?,
            currency = ?,
            capitalization = ?,
            auto_renewal = ?
        WHERE id = ?
        """
        return self.execute(
            sql,
            (
                depositor_id,
                deposit_type,
                amount,
                interest_rate,
                start_date,
                end_date,
                status,
                currency,
                capitalization,
                auto_renewal,
                deposit_id,
            ),
        )

    def delete_deposit(self, deposit_id: int):
        sql = "DELETE FROM deposits WHERE id = ?"
        return self.execute(sql, (deposit_id,))

    def get_by_id(self, deposit_id: int):
        sql = """
        SELECT
            d.id,
            d.depositor_id,
            d.opened_by_user_id,
            d.deposit_type,
            d.amount,
            d.interest_rate,
            d.currency,
            d.start_date,
            d.end_date,
            d.status,
            d.capitalization,
            d.auto_renewal,
            d.created_at,
            dep.lastname,
            dep.firstname,
            dep.middlename,
            u.user_name AS opened_by_user_name
        FROM deposits d
        JOIN depositors dep ON dep.id = d.depositor_id
        JOIN users u ON u.id = d.opened_by_user_id
        WHERE d.id = ?
        """
        return self.fetch_one(sql, (deposit_id,))

    def list_deposits(self):
        sql = """
        SELECT
            d.id,
            d.depositor_id,
            d.deposit_type,
            d.amount,
            d.interest_rate,
            d.currency,
            d.start_date,
            d.end_date,
            d.status,
            d.capitalization,
            d.auto_renewal,
            dep.last_name,
            dep.first_name,
            dep.middle_name
        FROM deposits d
        JOIN depositors dep ON dep.id = d.depositor_id
        ORDER BY d.id DESC
        """
        return self.fetch_all(sql)

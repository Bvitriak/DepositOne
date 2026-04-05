from __future__ import annotations
from core_service.app.models.base import BaseModel

class ContractModel(BaseModel):
    table_name = "contracts"

    def count_by_contract_date(self, contract_date: str):
        sql = """
            SELECT COUNT(*) AS cnt
            FROM contracts
            WHERE contract_date = ?
        """
        return self.fetch_one(sql, (contract_date,))

    def find_by_deposit_id(self, deposit_id: int):
        sql = """
            SELECT id, contract_number, deposit_id
            FROM contracts
            WHERE deposit_id = ?
            LIMIT 1
        """
        return self.fetch_one(sql, (deposit_id,))

    def deposit_exists(self, deposit_id: int) -> bool:
        sql = """
            SELECT id
            FROM deposits
            WHERE id = ?
            LIMIT 1
        """
        row = self.fetch_one(sql, (deposit_id,))
        return row is not None

    def create_contract(
        self,
        deposit_id: int,
        created_by_user_id: int,
        contract_number: str,
        contract_date: str,
        term_description: str | None = None,
        special_conditions: str | None = None,
        is_signed: int = 0,
    ):
        sql = """
            INSERT INTO contracts (
                deposit_id,
                created_by_user_id,
                contract_number,
                contract_date,
                term_description,
                special_conditions,
                is_signed
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute(
            sql,
            (
                deposit_id,
                created_by_user_id,
                contract_number,
                contract_date,
                term_description,
                special_conditions,
                is_signed,
            ),
        )

    def get_by_contract_number(self, contract_number: str):
        sql = """
            SELECT
                id,
                deposit_id,
                created_by_user_id,
                contract_number,
                contract_date,
                term_description,
                special_conditions,
                is_signed,
                created_at
            FROM contracts
            WHERE contract_number = ?
            LIMIT 1
        """
        return self.fetch_one(sql, (contract_number,))

    def get_contract_data(self, contract_id: int):
        sql = """
            SELECT
                c.contract_number,
                c.contract_date,
                c.special_conditions,
                d.id AS deposit_id,
                d.deposit_type,
                d.amount,
                d.interest_rate,
                d.start_date,
                d.end_date,
                d.capitalization,
                d.auto_renewal,
                dep.lastname AS last_name,
                dep.firstname AS first_name,
                dep.middlename AS middle_name,
                dep.passportseries AS passport_series,
                dep.passportnumber AS passport_number,
                dep.address,
                dep.phone
            FROM contracts c
            JOIN deposits d ON d.id = c.deposit_id
            JOIN depositors dep ON dep.id = d.depositor_id
            WHERE c.id = ?
        """
        return self.fetch_one(sql, (contract_id,))

from __future__ import annotations
from core_service.app.models.base import BaseModel

class DepositorModel(BaseModel):
    table_name = "depositors"

    def create_depositor(
        self,
        created_by_user_id: int,
        last_name: str,
        first_name: str,
        middle_name: str | None,
        passport_series: str,
        passport_number: str,
        issued_by: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        address: str | None = None,
    ):
        sql = """
            INSERT INTO depositors (
                createdbyuserid,
                lastname,
                firstname,
                middlename,
                passportseries,
                passportnumber,
                issuedby,
                phone,
                email,
                address
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute(
            sql,
            (
                created_by_user_id,
                last_name,
                first_name,
                middle_name,
                passport_series,
                passport_number,
                issued_by,
                phone,
                email,
                address,
            ),
        )

    def update_depositor(
        self,
        depositor_id: int,
        last_name: str,
        first_name: str,
        middle_name: str | None,
        passport_series: str,
        passport_number: str,
        issued_by: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        address: str | None = None,
    ):
        sql = """
        UPDATE depositors
        SET
            lastname = ?,
            firstname = ?,
            middlename = ?,
            passportseries = ?,
            passportnumber = ?,
            issuedby = ?,
            phone = ?,
            email = ?,
            address = ?
        WHERE id = ?
        """
        return self.execute(
            sql,
            (
                last_name,
                first_name,
                middle_name,
                passport_series,
                passport_number,
                issued_by,
                phone,
                email,
                address,
                depositor_id,
            ),
        )

    def delete_depositor(self, depositor_id: int):
        sql = "DELETE FROM depositors WHERE id = ?"
        return self.execute(sql, (depositor_id,))

    def get_by_id(self, depositor_id: int):
        sql = """
        SELECT
            d.id,
            d.lastname,
            d.firstname,
            d.middlename,
            d.passportseries,
            d.passportnumber,
            d.issuedby,
            d.phone,
            d.email,
            d.address,
            d.createdat
        FROM depositors d
        WHERE d.id = ?
        """
        return self.fetch_one(sql, (depositor_id,))

    def list_for_select(self):
        sql = """
        SELECT id, lastname, firstname, middlename
        FROM depositors
        ORDER BY lastname ASC, firstname ASC, id ASC
        """
        return self.fetch_all(sql)

from datetime import date, timedelta

from repositories import notification_repository

UPCOMING_DAYS = 7


def get_notifications(connection):
    today = date.today()
    notifications = []
    for row in notification_repository.upcoming_payouts(connection, today, today + timedelta(days=UPCOMING_DAYS)):
        name = row[0] + " " + row[1]
        notifications.append({
            "type": "payout",
            "message": "Deposit of " + name + " matures on " + row[2].isoformat(),
            "date": row[2].isoformat(),
        })
    for row in notification_repository.pending_contracts(connection):
        name = row[0] + " " + row[1]
        notifications.append({
            "type": "contract",
            "message": "Contract of " + name + " is waiting to be signed",
            "date": row[2].isoformat(),
        })
    return {"notifications": notifications}

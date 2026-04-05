from datetime import datetime
from supporting_service.constants import (DEFAULT_NOTIFICATION_CHANNEL, MODULE_NOTIFICATIONS, SERVICE_NAME )
from supporting_service.utils.fallbacks import business_error, exception_fallback, success

def send_notification(payload):
    try:
        channel = payload.channel
        recipient = payload.recipient.strip()
        subject = payload.subject.strip()
        message = payload.message.strip()

        if not recipient:
            return business_error(SERVICE_NAME, MODULE_NOTIFICATIONS, "Получатель обязателен.")
        if not message:
            return business_error(SERVICE_NAME, MODULE_NOTIFICATIONS, "Текст уведомления обязателен.")

        return success(
            SERVICE_NAME,
            MODULE_NOTIFICATIONS,
            {
                "notification_id": f"notif-{int(datetime.now().timestamp())}",
                "channel": channel or DEFAULT_NOTIFICATION_CHANNEL,
                "recipient": recipient,
                "subject": subject,
                "message": message,
                "status": "queued",
                "created_at": datetime.now().isoformat(),
            },
            "Уведомление поставлено в очередь.",
        )
    except AttributeError as exc:
        return exception_fallback(
            SERVICE_NAME,
            MODULE_NOTIFICATIONS,
            exc,
            fallback_data={
                "notification_id": None,
                "channel": getattr(payload, "channel", DEFAULT_NOTIFICATION_CHANNEL),
                "recipient": getattr(payload, "recipient", ""),
                "subject": getattr(payload, "subject", ""),
                "message": getattr(payload, "message", ""),
                "status": "failed",
                "created_at": None,
            },
            default_message="Ошибка при подготовке уведомления.",
        )

import requests
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


def send_connection_request(
    connection_id: int,
    sender_name: str,
    sender_emp_code: str,
    receiver_name: str,
    receiver_emp_code: str
):
    """
    Push interactive message to Synology Chat
    We use an Incoming Webhook to send to the user.
    """
    if not settings.SYNOLOGY_WEBHOOK_URL:
        logger.warning("SYNOLOGY_WEBHOOK_URL is not set. Skipping chat push.")
        return False

    payload = {
        "text": f"🔔 **Yêu cầu kết nối mới**\nChào {receiver_name}, tân binh **{sender_name}** ({sender_emp_code}) vừa rủ rê bạn kết nối để hoàn thành chỉ tiêu hội nhập!",
        "attachments": [
            {
                "callback_id": f"conn_request_{connection_id}",
                "text": "Bạn có muốn đồng ý kết nối ngay không?",
                "actions": [
                    {
                        "type": "button",
                        "name": "action",
                        "value": "accept",
                        "text": "Đồng Ý Trực Tiếp",
                        "style": "primary"
                    },
                    {
                        "type": "button",
                        "name": "action",
                        "value": "reject",
                        "text": "Để sau",
                        "style": "danger"
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(
            settings.SYNOLOGY_WEBHOOK_URL,
            json=payload,
            timeout=5.0
        )
        response.raise_for_status()
        logger.info(f"Pushed to Synology Chat successfully for conn_id={connection_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to push to Synology Chat: {e}")
        return False


def send_congratulations_message(
    emp_name: str,
    emp_code: str,
    days_to_complete: int,
    rank: int,
    target_month: int,
    target_year: int,
    role_label: str = "Staff"
):
    """
    Send a congratulations message to Synology Chat channel when an employee
    completes their connection target within the deadline.

    Args:
        emp_name: Full name of the employee who completed the target
        emp_code: Employee code
        days_to_complete: Number of days taken to complete all connections
        rank: Current rank on the monthly leaderboard
        target_month: Month of completion (1-12)
        target_year: Year of completion
        role_label: 'Operator' or 'Staff'
    """
    if not settings.SYNOLOGY_WEBHOOK_URL:
        logger.warning("SYNOLOGY_WEBHOOK_URL is not set. Skipping congratulations push.")
        return False

    # Medal emoji by rank
    medal = ""
    if rank == 1:
        medal = "🥇"
    elif rank == 2:
        medal = "🥈"
    elif rank == 3:
        medal = "🥉"
    else:
        medal = f"#{rank}"

    role_emoji = "🔧" if role_label == "Operator" else "💼"

    payload = {
        "text": (
            f"🎉 **CHÚC MỪNG HOÀN THÀNH NHIỆM VỤ!** 🎉\n\n"
            f"{role_emoji} **{emp_name}** ({emp_code}) — {role_label}\n"
            f"✅ Đã kết nối đủ chỉ tiêu trong **{days_to_complete} ngày**!\n"
            f"📅 Tháng {target_month:02d}/{target_year} — Hạng: {medal}\n\n"
            f"Cảm ơn bạn đã tích cực tham gia hội nhập vào đại gia đình CSB! 💪"
        )
    }

    try:
        response = requests.post(
            settings.SYNOLOGY_WEBHOOK_URL,
            json=payload,
            timeout=5.0
        )
        response.raise_for_status()
        logger.info(f"Congratulations message sent for {emp_code} (rank={rank})")
        return True
    except Exception as e:
        logger.error(f"Failed to send congratulations to Synology Chat: {e}")
        return False

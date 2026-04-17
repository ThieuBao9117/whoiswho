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

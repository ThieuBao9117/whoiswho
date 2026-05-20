from fastapi import APIRouter, Request, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
import json
import logging

from app.core.database import get_db
from app.models.crw_models import CRWConnection, ConnectionStatus

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/synology/callback")
async def synology_webhook_callback(request: Request, db: Session = Depends(get_db)):
    """
    Receive Outgoing Webhook / Action callback from Synology Chat.
    Synology sends form-urlencoded data: payload={"action":"accept","callback_id":"conn_request_123",...}
    """
    try:
        # Synology sends data as x-www-form-urlencoded with a 'payload' field containing JSON
        form_data = await request.form()
        payload_str = form_data.get("payload")
        
        if not payload_str:
            return {"status": "error", "message": "Missing payload"}
            
        payload = json.loads(payload_str)
        callback_id = payload.get("callback_id", "")
        action = payload.get("action", {}).get("value")
        
        # Parse connection_id
        if not callback_id.startswith("conn_request_"):
            return {"status": "ignored"}
            
        conn_id_str = callback_id.replace("conn_request_", "")
        try:
            conn_id = int(conn_id_str)
        except ValueError:
            return {"status": "error", "message": "Invalid connection ID format"}
            
        # Update DB
        conn = db.query(CRWConnection).filter(CRWConnection.id == conn_id).first()
        if not conn:
            return {"status": "error", "message": "Connection not found"}
            
        if action == "accept":
            conn.status = ConnectionStatus.ACCEPTED
        elif action == "reject":
            conn.status = ConnectionStatus.REJECTED
            
        conn.responded_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Synology Callback: Connection {conn_id} marked as {action}")
        
        # Return a message back to Synology Chat to replace the buttons with a status text
        if action == "accept":
            return {"text": "✅ Đã duyệt kết nối thành công từ điện thoại!"}
        return {"text": "❌ Đã từ chối lời mời."}
        
    except Exception as e:
        logger.error(f"Error handling synology webhook: {e}")
        return {"status": "error", "message": str(e)}

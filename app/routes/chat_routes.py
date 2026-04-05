from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.message_model import Message
from app.models.user_model import User
from datetime import datetime, timezone, timedelta

chat_bp = Blueprint("chat", __name__)

# =========================
# GET PREVIOUS MESSAGES
# =========================
@chat_bp.route("/<int:channel_id>/messages", methods=["GET"])
@jwt_required(optional=True)
def get_messages(channel_id):
    limit = request.args.get("limit", 10, type=int)
    offset = request.args.get("offset", 0, type=int)

    # Compute today's boundaries in IST (UTC+5:30) then convert to UTC for DB query
    # Messages are stored in UTC via datetime.utcnow()
    IST = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(IST)

    # Start of today in IST → convert to UTC
    today_ist_start = now_ist.replace(hour=0, minute=0, second=0, microsecond=0)
    today_ist_end   = now_ist.replace(hour=23, minute=59, second=59, microsecond=999999)

    day_start_utc = today_ist_start.astimezone(timezone.utc).replace(tzinfo=None)
    day_end_utc   = today_ist_end.astimezone(timezone.utc).replace(tzinfo=None)

    messages = Message.query \
        .filter_by(channel_id=channel_id) \
        .filter(Message.created_at >= day_start_utc) \
        .filter(Message.created_at <= day_end_utc) \
        .order_by(Message.created_at.desc()) \
        .offset(offset) \
        .limit(limit) \
        .all()

    result = []
    for msg in messages:
        user = User.query.get(msg.user_id)
        result.append({
            "id": str(msg.id),
            "user_id": str(msg.user_id),
            "username": user.username if user else "Unknown",
            "message": msg.message,
            "created_at": msg.created_at.isoformat() + "Z",  # 'Z' = UTC
        })

    return jsonify(result[::-1]), 200  # reverse for oldest → newest

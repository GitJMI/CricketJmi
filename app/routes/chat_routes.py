from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.message_model import Message
from app.models.user_model import User
from datetime import datetime, timezone

chat_bp = Blueprint("chat", __name__)

# =========================
# GET PREVIOUS MESSAGES
# =========================
@chat_bp.route("/<int:channel_id>/messages", methods=["GET"])
@jwt_required()
def get_messages(channel_id):
    limit = request.args.get("limit", 10, type=int)
    offset = request.args.get("offset", 0, type=int)

    # Only fetch today's messages (UTC date)
    today = datetime.now(timezone.utc).date()
    day_start = datetime(today.year, today.month, today.day, 0, 0, 0)
    day_end   = datetime(today.year, today.month, today.day, 23, 59, 59)

    messages = Message.query \
        .filter_by(channel_id=channel_id) \
        .filter(Message.created_at >= day_start) \
        .filter(Message.created_at <= day_end) \
        .order_by(Message.created_at.desc()) \
        .offset(offset) \
        .limit(limit) \
        .all()

    result = []
    for msg in messages:
        user = User.query.get(msg.user_id)
        result.append({
            "id": msg.id,
            "user_id": msg.user_id,
            "username": user.username if user else "Unknown",
            "message": msg.message,
            "created_at": msg.created_at.isoformat(),
        })

    return jsonify(result[::-1]), 200  # reverse for oldest → newest
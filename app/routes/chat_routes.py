from flask import Blueprint,request
from flask_jwt_extended import jwt_required
from app.models.message_model import Message
from app.models.user_model import User

chat_bp = Blueprint("chat", __name__)

# =========================
# GET PREVIOUS MESSAGES
# =========================
@chat_bp.route("/<int:channel_id>/messages", methods=["GET"])
@jwt_required()
def get_messages(channel_id):
    limit = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)

    messages = Message.query.filter_by(channel_id=channel_id) \
        .order_by(Message.created_at.desc()) \
        .offset(offset) \
        .limit(limit) \
        .all()

    result = []

    for msg in messages:
        user = User.query.get(msg.user_id )
        result.append({
            "user_id": msg.user_id,
            "username": user.username,
            "message": msg.message,
            "created_at": msg.created_at,

        })

    return result[::-1], 200  # reverse for oldest → newest
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask import request
from flask_jwt_extended import decode_token
from app.models.user_model import User
from app.extensions import db
from app.models.message_model import Message
import time

user_last_message_time = {}  # { user_id: timestamp }
MESSAGE_COOLDOWN = 2  # seconds
socketio = SocketIO()

# =========================
# IN-MEMORY STORAGE
# =========================
channel_users = {}      # { room: set(user_ids OR sids) }
sid_user_map = {}       # { sid: user_id }
sid_room_map = {}       # { sid: room }


def init_socket(app):
    socketio.init_app(
        app,
        cors_allowed_origins=app.config.get("SOCKET_CORS_ORIGINS", []),
    )

    # =========================
    # JOIN ROOM (CHANNEL)
    # =========================
    @socketio.on("join")
    def handle_join(data):
        token = data.get("token")  # optional
        channel_id = data.get("channel_id")

        user_id = None

        # Try decoding token (optional)
        if token:
            if token.startswith("Bearer "):
                token = token.split(" ")[1]
            try:
                decoded = decode_token(token)
                user_id = str(decoded["sub"])
            except Exception:
                pass  # ignore invalid token

        room = f"channel_{channel_id}"
        join_room(room)

        # Initialize room if not exists
        if room not in channel_users:
            channel_users[room] = set()

        # Track user (logged-in users only OR include guests below)
        if user_id:
            channel_users[room].add(user_id)
        else:
            channel_users[room].add(request.sid)  # track guest by session

        # Store mappings
        sid_user_map[request.sid] = user_id
        sid_room_map[request.sid] = room

        # Broadcast updated online count
        emit("online_users", {
            "channel_id": channel_id,
            "count": len(channel_users[room])
        }, room=room)

    # =========================
    # LEAVE ROOM
    # =========================
    @socketio.on("leave")
    def handle_leave(data):
        sid = request.sid
        room = sid_room_map.get(sid)

        if room:
            leave_room(room)
            remove_user(sid, room)

    # =========================
    # DISCONNECT
    # =========================
    @socketio.on("disconnect")
    def handle_disconnect():
        sid = request.sid
        room = sid_room_map.get(sid)

        if room:
            remove_user(sid, room)

    # =========================
    # SEND MESSAGE (LOGIN REQUIRED)
    # =========================
@socketio.on("send_message")
def handle_message(data):
    token = data.get("token")
    channel_id = data.get("channel_id")
    message_text = data.get("message")

    # Require login
    if not token:
        emit("error", {"msg": "Login required to send messages"})
        return

    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    try:
        decoded = decode_token(token)
        user_id = str(decoded["sub"])
    except Exception as e:
        emit("error", {"msg": f"Invalid token: {str(e)}"})
        return

    # Fetch user
    user = User.query.get(user_id)

    if not user:
        emit("error", {"msg": "User not found"})
        return

    room = f"channel_{channel_id}"
    current_time = time.time()
    last_time = user_last_message_time.get(user_id, 0)

    if current_time - last_time < MESSAGE_COOLDOWN:
        emit("error", {"msg": "You're sending messages too fast"})
        return

    user_last_message_time[user_id] = current_time
    
    # Save message
    msg = Message(
        user_id=user_id,
        channel_id=channel_id,
        message=message_text
    )

    db.session.add(msg)
    db.session.commit()

    # Broadcast with username
    emit("receive_message", {
        "id": msg.id,
        "user_id": user_id,
        "username": user.username,
        "message": message_text,
        "created_at": msg.created_at.isoformat() + "Z",
    }, room=room)
# =========================
# HELPER FUNCTION
# =========================
def remove_user(sid, room):
    user_id = sid_user_map.get(sid)

    if room in channel_users:
        if user_id:
            channel_users[room].discard(user_id)
        else:
            channel_users[room].discard(sid)

        # Broadcast updated count
        emit("online_users", {
            "count": len(channel_users[room])
        }, room=room)

    # Cleanup maps
    sid_user_map.pop(sid, None)
    sid_room_map.pop(sid, None)
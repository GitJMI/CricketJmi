from flask import Blueprint, jsonify, request
from app.models.channel_model import Channel
from flask_jwt_extended import jwt_required, get_jwt
from app.utils.decorators import subscription_required
from app.extensions import db

channel_bp = Blueprint("channels", __name__)

# =========================
# GET ALL CHANNELS
# =========================
@channel_bp.route("/", methods=["GET"])
@jwt_required(optional=True)
def get_channels():
    jwt_data = get_jwt()
    is_admin = False
    
    if jwt_data and jwt_data.get("role") == "admin":
        is_admin = True

    if is_admin:
        channels = Channel.query.order_by(Channel.id).all()
    else:
        channels = Channel.query.filter_by(is_active=True).order_by(Channel.id).all()

    result = []
    for ch in channels:
        result.append({
            "id": ch.id,
            "name": ch.name,
            "type": ch.type,
            "is_active": ch.is_active
        })

    return jsonify(result), 200


# =========================
# GET SINGLE CHANNEL
# =========================
@channel_bp.route("/<int:channel_id>", methods=["GET"])
@jwt_required(optional=True)
def get_channel(channel_id):
    ch = Channel.query.get(channel_id)

    if not ch:
        return {"error": "Channel not found"}, 404

    if not ch.is_active:
        jwt_data = get_jwt()
        if not jwt_data or jwt_data.get("role") != "admin":
            return {"error": "Channel is not accessible"}, 403

    return {
        "id": ch.id,
        "name": ch.name,
        "type": ch.type,
        "iframe_url": ch.iframe_url
    }, 200

# =========================
# EDIT CHANNEL (ADMIN ONLY)
# =========================
@channel_bp.route("/<int:channel_id>", methods=["PUT"])
@jwt_required()
def update_channel(channel_id):
    jwt_data = get_jwt()
    if jwt_data.get("role") != "admin":
        return {"error": "Admin access required"}, 403

    ch = Channel.query.get(channel_id)
    if not ch:
        return {"error": "Channel not found"}, 404

    data = request.get_json()
    
    if "name" in data:
        ch.name = data["name"]
        
    if "is_active" in data:
        ch.is_active = data["is_active"]
        
    db.session.commit()
    
    return {
        "message": "Channel updated successfully",
        "channel": {
            "id": ch.id,
            "name": ch.name,
            "type": ch.type,
            "is_active": ch.is_active
        }
    }, 200
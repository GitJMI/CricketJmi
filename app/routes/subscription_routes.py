from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.subscription_service import create_subscription, is_user_subscribed

subscription_bp = Blueprint("subscriptions", __name__)

# =========================
# BUY SUBSCRIPTION
# =========================
@subscription_bp.route("/buy", methods=["POST"])
@jwt_required()
def buy_subscription():
    user_id = get_jwt_identity()
    data = request.json

    plan = data.get("plan", "basic")

    sub = create_subscription(user_id, plan)
    #payment here , 
    
    return {
        "message": "Subscription activated",
        "plan": sub.plan,
        "expires_at": sub.end_date
    }, 201


# =========================
# CHECK SUBSCRIPTION
# =========================
@subscription_bp.route("/status", methods=["GET"])
@jwt_required()
def check_subscription():
    user_id = get_jwt_identity()

    active = is_user_subscribed(user_id)

    return {"active": active}
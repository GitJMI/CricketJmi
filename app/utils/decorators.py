from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.services.subscription_service import is_user_subscribed

def subscription_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()

        if not is_user_subscribed(user_id):
            return {"error": "Active subscription required"}, 403

        return fn(*args, **kwargs)

    return wrapper
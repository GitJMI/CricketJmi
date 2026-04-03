from app.models.subscription_model import Subscription
from app.extensions import db
from datetime import datetime, timedelta

def create_subscription(user_id, plan):
    duration_days = 1 if plan == "basic" else 3

    sub = Subscription(
        user_id=user_id,
        plan=plan,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=duration_days),
        status="active"
    )

    db.session.add(sub)
    db.session.commit()

    return sub


def get_user_subscription(user_id):
    return Subscription.query.filter_by(user_id=user_id).order_by(Subscription.id.desc()).first()


def is_user_subscribed(user_id):
    sub = get_user_subscription(user_id)

    if not sub:
        return False

    return sub.is_active()
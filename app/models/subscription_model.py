from app.extensions import db
from datetime import datetime, timedelta

class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), nullable=False)
    plan = db.Column(db.String(50))  # basic, premium
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="active")  # active, expired

    def is_active(self):
        return self.status == "active" and self.end_date > datetime.utcnow()
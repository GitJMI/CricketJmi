from app.extensions import db

class Channel(db.Model):
    __tablename__ = "channels"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(100))
    name = db.Column(db.String(100))
    type = db.Column(db.String(20), default="iframe")
    iframe_url = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
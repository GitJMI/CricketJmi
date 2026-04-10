from app.extensions import db
from datetime import datetime
import uuid

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(100) , unique = True )
    email = db.Column(db.String(255),unique = True)
    password_hash = db.Column(db.Text)
    created_at = db.Column(db.DateTime , default = datetime.utcnow)
    role = db.Column(db.Enum('client', 'admin', name='user_roles'), nullable=False, default='client')
    #role = db.Column(db.String(20), default="user")
    
    
    #checking the commit 
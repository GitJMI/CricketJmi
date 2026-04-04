from app.models.user_model import User
from app.extensions import db
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

def register_user(data):
    # Hash password using werkzeug
    password_hash = generate_password_hash(data['password'])

    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=password_hash
    )

    db.session.add(user)
    db.session.commit()

    # Automatically issue token to log them in directly
    token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role,
            "username": user.username,
            "email": user.email,
        }
    )

    return {"message": "User created successfully", "token": token}, 201


def login_user(data):
    user = User.query.filter_by(email=data['email']).first()

    if not user:
        return {"error": "User not found"}, 404

    # Verify password
    if not check_password_hash(user.password_hash, data['password']):
        return {"error": "Invalid credentials"}, 401

    token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role,
            "username": user.username,
            "email": user.email,
        }
    )

    return {"token": token}, 200
from app.models.user_model import User
from app.extensions import db
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

def register_user(data):
    # Validate required fields
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return {"message": "Username, email and password are required"}, 400

    # Check for existing user before attempting insert
    if User.query.filter_by(email=data['email']).first():
        return {"message": "An account with this email already exists"}, 409

    if User.query.filter_by(username=data['username']).first():
        return {"message": "This username is already taken"}, 409

    # Hash password using werkzeug
    password_hash = generate_password_hash(data['password'])

    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=password_hash
    )

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"message": "An account with this email or username already exists"}, 409

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
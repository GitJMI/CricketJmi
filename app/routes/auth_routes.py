from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_service import register_user, login_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
@jwt_required(optional=True)
def register():
    if get_jwt_identity():
        return jsonify({"message": "You are already logged in"}), 400
    data = request.json
    return register_user(data)

@auth_bp.route("/login", methods=["POST"])
@jwt_required(optional=True)
def login():
    if get_jwt_identity():
        return jsonify({"message": "You are already logged in"}), 400
    data = request.json
    return login_user(data)
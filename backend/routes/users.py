from flask import Blueprint, request, jsonify
from models import db, User

users_bp = Blueprint('users', __name__)

@users_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    
    email = data.get('email')
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists with this email"}), 400
        
    new_user = User(
        full_name=data.get('full_name'),
        email=email,
        mobile_number=data.get('mobile_number'),
        location=data.get('location'),
        preferred_categories=data.get('preferred_categories'),
        experience_level=data.get('experience_level'),
        preferred_work_type=data.get('preferred_work_type')
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        "message": "User profile created successfully",
        "user_id": new_user.id
    }), 201

@users_bp.route('/profile', methods=['GET'])
def get_profile():
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Email parameter required"}), 400
        
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    return jsonify({
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "mobile_number": user.mobile_number,
        "location": user.location,
        "preferred_categories": user.preferred_categories,
        "experience_level": user.experience_level,
        "preferred_work_type": user.preferred_work_type
    }), 200

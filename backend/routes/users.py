from flask import Blueprint, request, jsonify
from models import db, User, Application, Job

users_bp = Blueprint('users', __name__)

@users_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    
    email = data.get('email')
    full_name = data.get('full_name')
    
    if not email:
        return jsonify({"success": False, "error": "Email is required"}), 400
    if not full_name:
        return jsonify({"success": False, "error": "Full name is required"}), 400
        
    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "error": "User already exists with this email"}), 400
        
    new_user = User(
        full_name=full_name,
        email=email,
        mobile_number=data.get('mobile_number'),
        location=data.get('location'),
        preferred_categories=data.get('preferred_categories'),
        experience_level=data.get('experience_level'),
        preferred_work_type=data.get('preferred_work_type'),
        resume_url=data.get('resume_url')
    )
    
    db.session.add(new_user)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Registration error:", e)
        return jsonify({"success": False, "error": "Failed to create user profile due to database error"}), 500
    
    return jsonify({
        "success": True,
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

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    return jsonify({
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "mobile_number": user.mobile_number,
        "location": user.location,
        "preferred_categories": user.preferred_categories.split(",") if user.preferred_categories else [],
        "experience_level": user.experience_level,
        "preferred_work_type": user.preferred_work_type,
        "resume_url": user.resume_url
    }), 200

@users_bp.route('/<int:user_id>/applications', methods=['GET'])
def get_user_applications(user_id):
    applications = Application.query.filter_by(user_id=user_id).order_by(Application.created_at.desc()).all()
    
    result = []
    for app in applications:
        job = Job.query.get(app.job_id)
        if job:
            result.append({
                "id": app.id,
                "job_id": job.id,
                "title": job.title,
                "company": job.company_name,
                "status": app.status,
                "date": app.created_at.strftime("%Y-%m-%d %H:%M")
            })
            
    return jsonify(result), 200

@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404
        
    data = request.get_json()
    
    if 'full_name' in data and not data['full_name']:
        return jsonify({"success": False, "error": "Full name cannot be empty"}), 400
        
    if 'full_name' in data: user.full_name = data['full_name']
    if 'mobile_number' in data: user.mobile_number = data['mobile_number']
    if 'location' in data: user.location = data['location']
    if 'preferred_categories' in data: user.preferred_categories = data['preferred_categories']
    if 'experience_level' in data: user.experience_level = data['experience_level']
    if 'preferred_work_type' in data: user.preferred_work_type = data['preferred_work_type']
    if 'resume_url' in data: user.resume_url = data['resume_url']
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Update error:", e)
        return jsonify({"success": False, "error": "Database error while updating profile"}), 500
        
    return jsonify({"success": True, "message": "Profile updated successfully"}), 200

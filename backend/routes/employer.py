from flask import Blueprint, request, jsonify
from models import db, Employer
import random

employer_bp = Blueprint('employer', __name__)

# Reusing the simple in-memory OTP approach for MVP
otp_store = {}

@employer_bp.route('/auth/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({"error": "Email is required"}), 400
        
    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp
    
    print(f"Employer OTP for {email} is {otp}")
    
    return jsonify({"message": "OTP sent successfully", "otp_debug": otp}), 200

@employer_bp.route('/auth/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    
    if not email or not otp:
        return jsonify({"error": "Email and OTP are required"}), 400
        
    if otp_store.get(email) == otp:
        del otp_store[email]
        
        employer = Employer.query.filter_by(email=email).first()
        is_new_employer = employer is None
        
        return jsonify({
            "message": "OTP verified successfully",
            "is_new_employer": is_new_employer,
            "email": email
        }), 200
        
    return jsonify({"error": "Invalid OTP"}), 400

@employer_bp.route('/register', methods=['POST'])
def register_employer():
    data = request.get_json()
    
    email = data.get('email')
    if Employer.query.filter_by(email=email).first():
        return jsonify({"error": "Employer already exists with this email"}), 400
        
    new_employer = Employer(
        company_name=data.get('company_name'),
        employer_name=data.get('employer_name'),
        email=email,
        mobile_number=data.get('mobile_number'),
        business_type=data.get('business_type'),
        business_location=data.get('business_location'),
        company_description=data.get('company_description'),
        hiring_categories=data.get('hiring_categories'),
        is_verified=False # Initial status is Unverified
    )
    
    db.session.add(new_employer)
    db.session.commit()
    
    return jsonify({
        "message": "Employer profile created successfully",
        "employer_id": new_employer.id
    }), 201

@employer_bp.route('/profile', methods=['GET', 'PUT'])
def profile():
    email = request.args.get('email') or request.get_json().get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400
        
    employer = Employer.query.filter_by(email=email).first()
    if not employer:
        return jsonify({"error": "Employer not found"}), 404
        
    if request.method == 'GET':
        return jsonify({
            "id": employer.id,
            "company_name": employer.company_name,
            "employer_name": employer.employer_name,
            "email": employer.email,
            "mobile_number": employer.mobile_number,
            "business_type": employer.business_type,
            "business_location": employer.business_location,
            "company_description": employer.company_description,
            "hiring_categories": employer.hiring_categories,
            "is_verified": employer.is_verified,
            "created_at": employer.created_at.isoformat()
        }), 200
        
    if request.method == 'PUT':
        data = request.get_json()
        employer.company_name = data.get('company_name', employer.company_name)
        employer.employer_name = data.get('employer_name', employer.employer_name)
        employer.mobile_number = data.get('mobile_number', employer.mobile_number)
        employer.business_type = data.get('business_type', employer.business_type)
        employer.business_location = data.get('business_location', employer.business_location)
        employer.company_description = data.get('company_description', employer.company_description)
        employer.hiring_categories = data.get('hiring_categories', employer.hiring_categories)
        
        db.session.commit()
        return jsonify({"message": "Employer profile updated successfully"}), 200

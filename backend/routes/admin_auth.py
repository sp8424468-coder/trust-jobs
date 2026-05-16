from flask import Blueprint, request, jsonify
from models import db, Admin
import random

admin_auth_bp = Blueprint('admin_auth', __name__)

# In-memory OTP store for MVP
otp_store = {}

@admin_auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({"error": "Email is required"}), 400
        
    admin = Admin.query.filter_by(email=email).first()
    if not admin:
        return jsonify({"error": "Unauthorized access. Admin not found."}), 403
        
    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp
    
    print(f"Admin OTP for {email} is {otp}")
    
    return jsonify({"message": "OTP sent successfully", "otp_debug": otp}), 200

@admin_auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    
    if not email or not otp:
        return jsonify({"error": "Email and OTP are required"}), 400
        
    if otp_store.get(email) == otp:
        del otp_store[email]
        
        admin = Admin.query.filter_by(email=email).first()
        if not admin:
            return jsonify({"error": "Admin not found"}), 404
            
        return jsonify({
            "message": "OTP verified successfully",
            "admin": {
                "id": admin.id,
                "email": admin.email,
                "full_name": admin.full_name,
                "role": admin.role
            }
        }), 200
        
    return jsonify({"error": "Invalid OTP"}), 400

from flask import Blueprint, request, jsonify
from models import db, User
import random

auth_bp = Blueprint('auth', __name__)

# In-memory OTP store for MVP
otp_store = {}

@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({"error": "Email is required"}), 400
        
    # Generate a 6-digit OTP
    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp
    
    # In a real app, send the OTP via email using an email service
    print(f"OTP for {email} is {otp}")
    
    return jsonify({"message": "OTP sent successfully", "otp_debug": otp}), 200

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    
    if not email or not otp:
        return jsonify({"error": "Email and OTP are required"}), 400
        
    if otp_store.get(email) == otp:
        # OTP is valid, clear it
        del otp_store[email]
        
        # Check if user exists, if not, they will need to register profile
        user = User.query.filter_by(email=email).first()
        is_new_user = user is None
        
        return jsonify({
            "message": "OTP verified successfully",
            "is_new_user": is_new_user,
            "email": email
        }), 200
        
    return jsonify({"error": "Invalid OTP"}), 400

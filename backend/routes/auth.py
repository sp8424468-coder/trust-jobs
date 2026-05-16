from flask import Blueprint, request, jsonify, current_app
from models import db, User
import random
import time
import resend

auth_bp = Blueprint('auth', __name__)

# In-memory OTP store for MVP
otp_store = {}

def get_email_html(otp):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f9fafb; padding: 40px 20px; margin: 0;">
        <div style="max-width: 500px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; padding: 40px 30px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); text-align: center;">
            <div style="background-color: #10b981; color: white; width: 48px; height: 48px; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; margin: 0 auto 24px auto; font-size: 24px; font-weight: bold;">T</div>
            <h1 style="font-size: 24px; font-weight: 800; color: #111827; margin: 0 0 16px 0;">Verify your email</h1>
            <p style="color: #4b5563; font-size: 16px; line-height: 1.5; margin: 0 0 32px 0;">Enter the following verification code to access your TrustJobs account. This code is valid for 5 minutes.</p>
            
            <div style="background-color: #f9fafb; border: 2px dashed #e5e7eb; border-radius: 12px; padding: 24px; font-size: 36px; font-weight: 900; letter-spacing: 8px; color: #10b981; margin: 0 0 32px 0;">{otp}</div>
            
            <p style="color: #6b7280; font-size: 14px; margin: 0;">If you didn't request this code, you can safely ignore this email.</p>
            <div style="margin-top: 32px; padding-top: 24px; border-top: 1px solid #e5e7eb;">
                <p style="color: #9ca3af; font-size: 12px; margin: 0;">© 2026 TrustJobs. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({"error": "Email is required"}), 400
        
    # Generate a 6-digit OTP
    otp = str(random.randint(100000, 999999))
    
    # Store OTP with 5 min expiration
    otp_store[email] = {
        "otp": otp,
        "expires_at": time.time() + 300
    }
    
    resend_api_key = current_app.config.get('RESEND_API_KEY')
    resend_from_email = current_app.config.get('RESEND_FROM_EMAIL', 'onboarding@resend.dev')
    
    if resend_api_key:
        resend.api_key = resend_api_key
        try:
            r = resend.Emails.send({
                "from": f"TrustJobs <{resend_from_email}>",
                "to": email,
                "subject": "TrustJobs Login Verification Code",
                "html": get_email_html(otp)
            })
            print("Resend response:", r)
        except Exception as e:
            print("Failed to send email via resend:", e)
            return jsonify({"error": "Failed to send OTP email"}), 500
    else:
        print(f"RESEND_API_KEY missing. OTP for {email} is {otp}")
        return jsonify({"error": "Email service not configured. Please add RESEND_API_KEY."}), 500
    
    return jsonify({"message": "OTP sent successfully"}), 200

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    
    if not email or not otp:
        return jsonify({"error": "Email and OTP are required"}), 400
        
    stored_data = otp_store.get(email)
    if not stored_data:
        return jsonify({"error": "No OTP requested for this email"}), 400
        
    if time.time() > stored_data["expires_at"]:
        del otp_store[email]
        return jsonify({"error": "OTP has expired"}), 400
        
    if stored_data["otp"] == otp:
        # OTP is valid, clear it
        del otp_store[email]
        
        # Check if user exists, if not, they will need to register profile
        user = User.query.filter_by(email=email).first()
        is_new_user = user is None
        
        if user:
            return jsonify({
                "success": True,
                "is_new_user": False,
                "user": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "email": user.email
                }
            }), 200
        else:
            return jsonify({
                "success": True,
                "is_new_user": True
            }), 200
        
    return jsonify({"error": "Invalid OTP"}), 400

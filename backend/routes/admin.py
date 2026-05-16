from flask import Blueprint, request, jsonify
from models import db, Admin, User, Employer, Job, Application, VerificationRequest, Notification
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
def get_dashboard_stats():
    admin_id = request.args.get('admin_id')
    if not admin_id:
        return jsonify({"error": "Admin ID required"}), 400

    total_users = User.query.count()
    total_employers = Employer.query.count()
    active_jobs = Job.query.filter_by(status='Published').count()
    total_applications = Application.query.count()
    verified_employers = Employer.query.filter_by(is_verified=True).count()
    pending_verifications = VerificationRequest.query.filter_by(status='Verification Pending').count()
    reported_jobs = Job.query.filter_by(is_reported=True).count()
    suspended_users = User.query.filter_by(is_suspended=True).count()
    suspended_employers = Employer.query.filter_by(is_suspended=True).count()
    
    return jsonify({
        "total_users": total_users,
        "total_employers": total_employers,
        "active_jobs": active_jobs,
        "total_applications": total_applications,
        "verified_employers": verified_employers,
        "pending_verifications": pending_verifications,
        "reported_jobs": reported_jobs,
        "suspended_accounts": suspended_users + suspended_employers
    }), 200

@admin_bp.route('/analytics', methods=['GET'])
def get_analytics():
    admin_id = request.args.get('admin_id')
    if not admin_id:
        return jsonify({"error": "Admin ID required"}), 400
        
    # Mock chart data for MVP
    # In a real app, group by date and count records
    today = datetime.utcnow()
    dates = [(today - timedelta(days=i)).strftime('%b %d') for i in range(6, -1, -1)]
    
    user_growth = [5, 12, 8, 15, 22, 18, 25]
    job_activity = [2, 4, 3, 7, 5, 8, 10]
    employer_growth = [1, 3, 2, 5, 4, 6, 8]
    
    # Calculate Verification Approval Rate
    total_reqs = VerificationRequest.query.count()
    approved_reqs = VerificationRequest.query.filter_by(status='Verified Employer').count()
    approval_rate = (approved_reqs / total_reqs * 100) if total_reqs > 0 else 85.5 # Fallback to 85.5% mock
    
    # Calculate Categories & Locations
    # For MVP we mock the complex GROUP BY queries
    categories = [
        {"name": "Delivery", "count": 145},
        {"name": "IT & Software", "count": 92},
        {"name": "Accountant", "count": 64},
        {"name": "Helper", "count": 48}
    ]
    
    locations = [
        {"name": "Mumbai", "count": 210},
        {"name": "Bangalore", "count": 185},
        {"name": "Delhi", "count": 150},
        {"name": "Pune", "count": 95}
    ]
    
    return jsonify({
        "labels": dates,
        "user_growth": user_growth,
        "job_activity": job_activity,
        "employer_growth": employer_growth,
        "verification_approval_rate": round(approval_rate, 1),
        "most_active_categories": categories,
        "top_hiring_locations": locations
    }), 200

@admin_bp.route('/notifications/send', methods=['POST'])
def send_notification():
    data = request.get_json()
    admin_id = data.get('admin_id')
    target = data.get('target_audience') # 'all', 'employers', 'users'
    message = data.get('message')
    
    if not admin_id or not target or not message:
        return jsonify({"error": "Missing required fields"}), 400
        
    notification = Notification(
        target_audience=target,
        message=message
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({"message": f"Notification sent successfully to {target}"}), 200

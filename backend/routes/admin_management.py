from flask import Blueprint, request, jsonify
from models import db, User, Employer, Job, Application, VerificationRequest, VerificationDocument
from sqlalchemy import func

admin_mgmt_bp = Blueprint('admin_mgmt', __name__)

# --- USERS MANAGEMENT ---

@admin_mgmt_bp.route('/users', methods=['GET'])
def get_users():
    search = request.args.get('search', '').lower()
    status = request.args.get('status', 'all')
    
    query = User.query
    
    if search:
        query = query.filter((func.lower(User.full_name).contains(search)) | (func.lower(User.email).contains(search)))
        
    if status == 'suspended':
        query = query.filter_by(is_suspended=True)
    elif status == 'active':
        query = query.filter_by(is_suspended=False)
        
    users = query.order_by(User.created_at.desc()).all()
    
    result = []
    for u in users:
        app_count = Application.query.filter_by(user_id=u.id).count()
        result.append({
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "mobile_number": u.mobile_number,
            "location": u.location,
            "is_suspended": u.is_suspended,
            "created_at": u.created_at.isoformat(),
            "applications_count": app_count
        })
        
    return jsonify(result), 200

@admin_mgmt_bp.route('/users/<int:user_id>/status', methods=['PUT'])
def update_user_status(user_id):
    data = request.get_json()
    action = data.get('action') # 'suspend', 'reactivate', 'delete'
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    if action == 'suspend':
        user.is_suspended = True
    elif action == 'reactivate':
        user.is_suspended = False
    elif action == 'delete':
        db.session.delete(user)
        
    db.session.commit()
    return jsonify({"message": f"User successfully {action}ed"}), 200


# --- EMPLOYERS MANAGEMENT ---

@admin_mgmt_bp.route('/employers', methods=['GET'])
def get_employers():
    search = request.args.get('search', '').lower()
    v_status = request.args.get('verification_status', 'all')
    
    query = Employer.query
    
    if search:
        query = query.filter((func.lower(Employer.company_name).contains(search)) | (func.lower(Employer.email).contains(search)))
        
    if v_status != 'all':
        query = query.filter_by(verification_status=v_status)
        
    employers = query.order_by(Employer.created_at.desc()).all()
    
    result = []
    for e in employers:
        active_jobs = Job.query.filter_by(employer_id=e.id, status='Published').count()
        apps_received = db.session.query(Application).join(Job).filter(Job.employer_id == e.id).count()
        result.append({
            "id": e.id,
            "company_name": e.company_name,
            "email": e.email,
            "location": e.location,
            "is_verified": e.is_verified,
            "verification_status": e.verification_status,
            "is_suspended": e.is_suspended,
            "created_at": e.created_at.isoformat(),
            "active_jobs": active_jobs,
            "applications_received": apps_received
        })
        
    return jsonify(result), 200

@admin_mgmt_bp.route('/employers/<int:employer_id>/status', methods=['PUT'])
def update_employer_status(employer_id):
    data = request.get_json()
    action = data.get('action') # 'approve', 'reject', 'suspend', 'reactivate'
    
    emp = Employer.query.get(employer_id)
    if not emp:
        return jsonify({"error": "Employer not found"}), 404
        
    if action == 'approve':
        emp.verification_status = 'Verified Employer'
        emp.is_verified = True
    elif action == 'reject':
        emp.verification_status = 'Rejected'
        emp.is_verified = False
    elif action == 'suspend':
        emp.is_suspended = True
    elif action == 'reactivate':
        emp.is_suspended = False
        
    db.session.commit()
    return jsonify({"message": f"Employer successfully {action}ed"}), 200


# --- JOBS MANAGEMENT ---

@admin_mgmt_bp.route('/jobs', methods=['GET'])
def get_jobs():
    search = request.args.get('search', '').lower()
    status = request.args.get('status', 'all')
    
    query = db.session.query(Job, Employer).join(Employer)
    
    if search:
        query = query.filter((func.lower(Job.title).contains(search)) | (func.lower(Employer.company_name).contains(search)))
        
    if status == 'Reported':
        query = query.filter(Job.is_reported == True)
    elif status != 'all':
        query = query.filter(Job.status == status)
        
    jobs = query.order_by(Job.created_at.desc()).all()
    
    result = []
    for job, emp in jobs:
        app_count = Application.query.filter_by(job_id=job.id).count()
        result.append({
            "id": job.id,
            "title": job.title,
            "category": job.category,
            "salary": job.salary,
            "location": job.location,
            "status": job.status,
            "is_reported": job.is_reported,
            "created_at": job.created_at.isoformat(),
            "employer_name": emp.company_name,
            "employer_verified": emp.is_verified,
            "applications_count": app_count
        })
        
    return jsonify(result), 200

@admin_mgmt_bp.route('/jobs/<int:job_id>/status', methods=['PUT'])
def update_job_status(job_id):
    data = request.get_json()
    action = data.get('action') # 'approve', 'remove', 'suspend', 'mark_suspicious'
    
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
        
    if action == 'approve':
        job.status = 'Published'
        job.is_reported = False
    elif action == 'remove':
        job.status = 'Deleted'
    elif action == 'suspend':
        job.status = 'Suspended'
    elif action == 'mark_suspicious':
        job.is_reported = True
        
    db.session.commit()
    return jsonify({"message": f"Job successfully updated"}), 200

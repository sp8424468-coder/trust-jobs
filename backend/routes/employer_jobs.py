from flask import Blueprint, request, jsonify
from models import db, Job, Application, User, Employer
from sqlalchemy import func

employer_jobs_bp = Blueprint('employer_jobs', __name__)

@employer_jobs_bp.route('/', methods=['GET'])
def get_employer_jobs():
    employer_id = request.args.get('employer_id')
    if not employer_id:
        return jsonify({"error": "employer_id is required"}), 400
        
    jobs = Job.query.filter_by(employer_id=employer_id).order_by(Job.created_at.desc()).all()
    
    result = []
    for job in jobs:
        applications_count = Application.query.filter_by(job_id=job.id).count()
        result.append({
            "id": job.id,
            "title": job.title,
            "category": job.category,
            "job_type": job.job_type,
            "status": job.status,
            "applications_count": applications_count,
            "views": job.views,
            "created_at": job.created_at.isoformat()
        })
        
    return jsonify(result), 200

@employer_jobs_bp.route('/', methods=['POST'])
def create_job():
    data = request.get_json()
    employer_id = data.get('employer_id')
    
    if not employer_id:
        return jsonify({"error": "employer_id is required"}), 400
        
    employer = Employer.query.get(employer_id)
    if not employer:
        return jsonify({"error": "Employer not found"}), 404
        
    new_job = Job(
        employer_id=employer_id,
        title=data.get('title'),
        company_name=employer.company_name,
        salary=data.get('salary'),
        location=data.get('location'),
        job_type=data.get('job_type'),
        category=data.get('category'),
        description=data.get('description'),
        experience_required=data.get('experience_required'),
        skills_required=data.get('skills_required'),
        work_type=data.get('work_type'),
        openings=data.get('openings', 1),
        contact_info=data.get('contact_info'),
        benefits=data.get('benefits'),
        working_hours=data.get('working_hours'),
        gender_preference=data.get('gender_preference'),
        accommodation_available=data.get('accommodation_available', False),
        status=data.get('status', 'Published'),
        is_verified_employer=employer.is_verified
    )
    
    db.session.add(new_job)
    db.session.commit()
    
    return jsonify({"message": "Job created successfully", "job_id": new_job.id}), 201

@employer_jobs_bp.route('/<int:job_id>', methods=['GET'])
def get_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    return jsonify({
        "id": job.id,
        "title": job.title,
        "company_name": job.company_name,
        "salary": job.salary,
        "location": job.location,
        "job_type": job.job_type,
        "category": job.category,
        "description": job.description,
        "experience_required": job.experience_required,
        "skills_required": job.skills_required,
        "work_type": job.work_type,
        "openings": job.openings,
        "contact_info": job.contact_info,
        "benefits": job.benefits,
        "working_hours": job.working_hours,
        "gender_preference": job.gender_preference,
        "accommodation_available": job.accommodation_available,
        "status": job.status
    }), 200

@employer_jobs_bp.route('/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
        
    data = request.get_json()
    
    # Update fields
    for key, value in data.items():
        if hasattr(job, key) and key not in ['id', 'employer_id', 'created_at', 'views', 'is_verified_employer', 'company_name']:
            setattr(job, key, value)
            
    db.session.commit()
    return jsonify({"message": "Job updated successfully"}), 200

@employer_jobs_bp.route('/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
        
    # Optional: could just mark as 'Deleted' instead of physical delete
    job.status = 'Deleted'
    db.session.commit()
    return jsonify({"message": "Job deleted successfully"}), 200

@employer_jobs_bp.route('/<int:job_id>/applicants', methods=['GET'])
def get_applicants(job_id):
    applications = Application.query.filter_by(job_id=job_id).all()
    
    result = []
    for app in applications:
        user = User.query.get(app.user_id)
        if user:
            result.append({
                "application_id": app.id,
                "user_id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "mobile_number": user.mobile_number,
                "resume_url": user.resume_url,
                "experience_level": user.experience_level,
                "status": app.status,
                "applied_at": app.created_at.isoformat()
            })
            
    return jsonify(result), 200

@employer_jobs_bp.route('/applications/<int:app_id>/status', methods=['PUT'])
def update_application_status(app_id):
    data = request.get_json()
    status = data.get('status')
    
    if not status:
        return jsonify({"error": "Status is required"}), 400
        
    application = Application.query.get(app_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404
        
    application.status = status
    db.session.commit()
    
    return jsonify({"message": f"Application status updated to {status}"}), 200

@employer_jobs_bp.route('/analytics', methods=['GET'])
def get_analytics():
    employer_id = request.args.get('employer_id')
    if not employer_id:
        return jsonify({"error": "employer_id is required"}), 400
        
    jobs = Job.query.filter_by(employer_id=employer_id).all()
    active_jobs = [j for j in jobs if j.status == 'Published']
    
    total_views = sum([j.views for j in jobs])
    
    job_ids = [j.id for j in jobs]
    total_applicants = Application.query.filter(Application.job_id.in_(job_ids) if job_ids else False).count()
    shortlisted_applicants = Application.query.filter(
        Application.job_id.in_(job_ids) if job_ids else False,
        Application.status.in_(['Shortlisted', 'Interview Scheduled'])
    ).count()
    
    return jsonify({
        "total_jobs": len(jobs),
        "active_jobs": len(active_jobs),
        "total_views": total_views,
        "total_applicants": total_applicants,
        "shortlisted_applicants": shortlisted_applicants
    }), 200

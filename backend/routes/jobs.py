from flask import Blueprint, request, jsonify
from models import db, Job

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/', methods=['GET'])
def get_jobs():
    category = request.args.get('category')
    location = request.args.get('location')
    
    query = Job.query
    
    if category:
        query = query.filter(Job.category.ilike(f'%{category}%'))
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
        
    jobs = query.all()
    
    jobs_list = []
    for job in jobs:
        jobs_list.append({
            "id": job.id,
            "title": job.title,
            "company_name": job.company_name,
            "salary": job.salary,
            "location": job.location,
            "job_type": job.job_type,
            "category": job.category,
            "is_verified_employer": job.is_verified_employer,
            "created_at": job.created_at.isoformat()
        })
        
    return jsonify({"jobs": jobs_list}), 200

@jobs_bp.route('/search', methods=['GET'])
def search_jobs():
    keyword = request.args.get('keyword')
    location = request.args.get('location')
    category = request.args.get('category')
    verified = request.args.get('verified')
    salary_min = request.args.get('salary_min', type=int)
    
    query = Job.query.filter(Job.status == 'Published')
    
    if keyword:
        search_filter = db.or_(
            Job.title.ilike(f'%{keyword}%'),
            Job.company_name.ilike(f'%{keyword}%'),
            Job.category.ilike(f'%{keyword}%')
        )
        query = query.filter(search_filter)
        
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
        
    if category:
        query = query.filter(Job.category.ilike(f'%{category}%'))
        
    if verified and verified.lower() == 'true':
        query = query.filter(Job.is_verified_employer == True)
        
    jobs = query.all()
    
    if salary_min is not None:
        import re
        def extract_min_salary(salary_str):
            if not salary_str: return 0
            s = salary_str.replace(',', '').lower()
            matches = re.findall(r'(\d+)(k?)', s)
            if matches:
                val = int(matches[0][0])
                if matches[0][1] == 'k':
                    val *= 1000
                elif val < 1000 and len(matches[0][0]) <= 3:
                    # For cases like "18k" where 'k' might be missing but value is low
                    # though usually they'd specify k. Let's just return val if not k.
                    pass
                return val
            return 0
        
        jobs = [j for j in jobs if extract_min_salary(j.salary) >= salary_min]
        
    jobs_list = []
    for job in jobs:
        jobs_list.append({
            "id": job.id,
            "title": job.title,
            "company_name": job.company_name,
            "salary": job.salary,
            "location": job.location,
            "job_type": job.job_type,
            "category": job.category,
            "is_verified_employer": job.is_verified_employer,
            "created_at": job.created_at.isoformat()
        })
        
    return jsonify({"jobs": jobs_list}), 200

@jobs_bp.route('/', methods=['POST'])
def create_job():
    data = request.get_json()
    
    new_job = Job(
        title=data.get('title'),
        company_name=data.get('company_name'),
        salary=data.get('salary'),
        location=data.get('location'),
        job_type=data.get('job_type'),
        category=data.get('category'),
        is_verified_employer=data.get('is_verified_employer', False)
    )
    
    db.session.add(new_job)
    db.session.commit()
    
    return jsonify({"message": "Job created successfully", "id": new_job.id}), 201

@jobs_bp.route('/<int:job_id>/apply', methods=['POST'])
def apply_job(job_id):
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "User ID required"}), 400
        
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
        
    # Check if already applied
    from models import Application
    existing = Application.query.filter_by(user_id=user_id, job_id=job_id).first()
    if existing:
        return jsonify({"error": "Already applied to this job"}), 400
        
    new_app = Application(
        user_id=user_id,
        job_id=job_id,
        status='Applied'
    )
    db.session.add(new_app)
    
    # Increment job applications counter or views if needed
    
    db.session.commit()
    
    return jsonify({"message": "Successfully applied to job!", "application_id": new_app.id}), 200


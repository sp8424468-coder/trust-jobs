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

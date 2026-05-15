from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile_number = db.Column(db.String(20), unique=True, nullable=True)
    location = db.Column(db.String(100), nullable=True)
    # comma separated or JSON for simplicity in MVP
    preferred_categories = db.Column(db.String(200), nullable=True)
    resume_url = db.Column(db.String(255), nullable=True)
    experience_level = db.Column(db.String(50), nullable=True)
    preferred_work_type = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    salary = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=False)
    job_type = db.Column(db.String(50), nullable=False) # Full-time, Part-time
    category = db.Column(db.String(100), nullable=False)
    is_verified_employer = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

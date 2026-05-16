from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Employer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150), nullable=False)
    employer_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile_number = db.Column(db.String(20), unique=True, nullable=True)
    business_type = db.Column(db.String(100), nullable=True)
    business_location = db.Column(db.String(100), nullable=True)
    company_description = db.Column(db.Text, nullable=True)
    company_logo_url = db.Column(db.String(255), nullable=True)
    hiring_categories = db.Column(db.String(200), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_status = db.Column(db.String(50), default='Unverified') # Unverified, Verification Pending, Verified Employer, Physically Verified
    is_suspended = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    is_suspended = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('employer.id'), nullable=True)
    title = db.Column(db.String(150), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    salary = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=False)
    job_type = db.Column(db.String(50), nullable=False) # Full-time, Part-time
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    experience_required = db.Column(db.String(100), nullable=True)
    skills_required = db.Column(db.String(255), nullable=True)
    work_type = db.Column(db.String(50), nullable=True) # On-site, Remote, Hybrid
    openings = db.Column(db.Integer, default=1)
    contact_info = db.Column(db.String(255), nullable=True)
    benefits = db.Column(db.Text, nullable=True)
    working_hours = db.Column(db.String(100), nullable=True)
    gender_preference = db.Column(db.String(50), nullable=True)
    accommodation_available = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(50), default='Published') # Draft, Published, Paused, Filled, Deleted, Reported
    views = db.Column(db.Integer, default=0)
    is_verified_employer = db.Column(db.Boolean, default=False)
    is_reported = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('employer.id'), nullable=True)
    target_audience = db.Column(db.String(50), nullable=True) # 'all', 'employers', 'users', or null for direct
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False) # Super Admin, Moderator, Verification Manager
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class VerificationRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('employer.id'), nullable=False)
    status = db.Column(db.String(50), default='Verification Pending')
    admin_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VerificationDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    verification_request_id = db.Column(db.Integer, db.ForeignKey('verification_request.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False) # GST, PAN, Business License, Office Photo
    document_url = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('employer.id'), nullable=True)
    reason = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='Pending') # Pending, Investigating, Resolved, Dismissed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    target_type = db.Column(db.String(50), nullable=False) # User, Employer, Job, Report, Verification
    target_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



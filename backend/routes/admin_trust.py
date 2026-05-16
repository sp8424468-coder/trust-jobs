from flask import Blueprint, request, jsonify
from models import db, VerificationRequest, VerificationDocument, Employer, Report, AuditLog, Job, User

admin_trust_bp = Blueprint('admin_trust', __name__)

def log_audit(admin_id, action, target_type, target_id, details=None):
    log = AuditLog(
        admin_id=admin_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details
    )
    db.session.add(log)
    db.session.commit()

# --- VERIFICATIONS ---

@admin_trust_bp.route('/verifications', methods=['GET'])
def get_verifications():
    status = request.args.get('status', 'all')
    
    query = VerificationRequest.query
    if status != 'all':
        query = query.filter_by(status=status)
        
    requests = query.order_by(VerificationRequest.created_at.desc()).all()
    
    result = []
    for req in requests:
        emp = Employer.query.get(req.employer_id)
        if emp:
            docs = VerificationDocument.query.filter_by(verification_request_id=req.id).all()
            result.append({
                "id": req.id,
                "employer_id": req.employer_id,
                "company_name": emp.company_name,
                "status": req.status,
                "created_at": req.created_at.isoformat(),
                "documents": [{"type": d.document_type, "url": d.document_url} for d in docs]
            })
            
    return jsonify(result), 200

# Endpoint to approve/reject is already in verification.py (we can keep it there, just need to log it)
# We will wrap it or just use the existing one and assume logging is handled here if we updated it.
# Wait, let's create a specific one here that includes logging.

@admin_trust_bp.route('/verifications/<int:req_id>/status', methods=['PUT'])
def update_verification_status():
    data = request.get_json()
    status = data.get('status')
    admin_id = data.get('admin_id')
    
    req = VerificationRequest.query.get(req_id)
    if not req:
        return jsonify({"error": "Not found"}), 404
        
    req.status = status
    emp = Employer.query.get(req.employer_id)
    if emp:
        emp.verification_status = status
        emp.is_verified = (status == 'Verified Employer')
        
    db.session.commit()
    
    if admin_id:
        log_audit(admin_id, f"Verification {status}", "Verification", req.id, f"Employer ID: {emp.id if emp else 'Unknown'}")
        
    return jsonify({"message": "Status updated"}), 200

# --- REPORTS ---

@admin_trust_bp.route('/reports', methods=['GET'])
def get_reports():
    status = request.args.get('status', 'Pending')
    
    query = Report.query
    if status != 'all':
        query = query.filter_by(status=status)
        
    reports = query.order_by(Report.created_at.desc()).all()
    
    result = []
    for r in reports:
        reporter = User.query.get(r.user_id)
        job = Job.query.get(r.job_id) if r.job_id else None
        emp = Employer.query.get(r.employer_id) if r.employer_id else None
        
        result.append({
            "id": r.id,
            "reason": r.reason,
            "details": r.details,
            "status": r.status,
            "created_at": r.created_at.isoformat(),
            "reporter_name": reporter.full_name if reporter else "Unknown",
            "target": job.title if job else (emp.company_name if emp else "Unknown Target"),
            "target_type": "Job" if job else "Employer"
        })
        
    return jsonify(result), 200

@admin_trust_bp.route('/reports/<int:report_id>/status', methods=['PUT'])
def update_report_status(report_id):
    data = request.get_json()
    status = data.get('status') # 'Investigating', 'Resolved', 'Dismissed'
    admin_id = data.get('admin_id')
    
    report = Report.query.get(report_id)
    if not report:
        return jsonify({"error": "Not found"}), 404
        
    report.status = status
    db.session.commit()
    
    if admin_id:
        log_audit(admin_id, f"Report {status}", "Report", report.id)
        
    return jsonify({"message": "Report status updated"}), 200

# --- AUDIT LOGS ---

@admin_trust_bp.route('/audit-logs', methods=['GET'])
def get_audit_logs():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(100).all()
    result = []
    for l in logs:
        # Avoid circular import, Admin might be imported if needed, just returning ID for now
        result.append({
            "id": l.id,
            "admin_id": l.admin_id,
            "action": l.action,
            "target_type": l.target_type,
            "target_id": l.target_id,
            "details": l.details,
            "created_at": l.created_at.isoformat()
        })
    return jsonify(result), 200

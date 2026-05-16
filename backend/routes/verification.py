from flask import Blueprint, request, jsonify
from models import db, VerificationRequest, VerificationDocument, Employer, Notification

verification_bp = Blueprint('verification', __name__)

@verification_bp.route('/upload', methods=['POST'])
def upload_documents():
    data = request.get_json()
    employer_id = data.get('employer_id')
    documents = data.get('documents') # list of dicts: {'type': 'GST', 'url': '...'}
    
    if not employer_id or not documents:
        return jsonify({"error": "employer_id and documents are required"}), 400
        
    employer = Employer.query.get(employer_id)
    if not employer:
        return jsonify({"error": "Employer not found"}), 404
        
    # Check if request already exists
    req = VerificationRequest.query.filter_by(employer_id=employer_id).first()
    if not req:
        req = VerificationRequest(employer_id=employer_id, status='Verification Pending')
        db.session.add(req)
        db.session.commit() # commit to get ID
    else:
        req.status = 'Verification Pending'
        
    for doc in documents:
        new_doc = VerificationDocument(
            verification_request_id=req.id,
            document_type=doc.get('type'),
            document_url=doc.get('url')
        )
        db.session.add(new_doc)
        
    employer.verification_status = 'Verification Pending'
    
    # Notify Admin (Simulation) and Employer
    notification = Notification(
        employer_id=employer_id,
        message="Your verification documents have been submitted and are under review."
    )
    db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({"message": "Documents uploaded successfully", "status": "Verification Pending"}), 200

@verification_bp.route('/status', methods=['GET'])
def get_status():
    employer_id = request.args.get('employer_id')
    if not employer_id:
        return jsonify({"error": "employer_id is required"}), 400
        
    employer = Employer.query.get(employer_id)
    if not employer:
        return jsonify({"error": "Employer not found"}), 404
        
    req = VerificationRequest.query.filter_by(employer_id=employer_id).first()
    documents = []
    
    if req:
        docs = VerificationDocument.query.filter_by(verification_request_id=req.id).all()
        for d in docs:
            documents.append({
                "type": d.document_type,
                "url": d.document_url,
                "uploaded_at": d.uploaded_at.isoformat()
            })
            
    return jsonify({
        "status": employer.verification_status,
        "admin_notes": req.admin_notes if req else None,
        "documents": documents
    }), 200

@verification_bp.route('/admin/approve', methods=['POST'])
def admin_approve():
    data = request.get_json()
    employer_id = data.get('employer_id')
    status = data.get('status') # 'Verified Employer' or 'Rejected'
    notes = data.get('notes')
    
    req = VerificationRequest.query.filter_by(employer_id=employer_id).first()
    employer = Employer.query.get(employer_id)
    
    if not req or not employer:
        return jsonify({"error": "Verification request not found"}), 404
        
    req.status = status
    req.admin_notes = notes
    employer.verification_status = status
    
    if status == 'Verified Employer':
        employer.is_verified = True
        
    # Send notification
    msg = "Your employer account has been successfully verified!" if status == 'Verified Employer' else f"Your verification was rejected. Reason: {notes}"
    notification = Notification(
        employer_id=employer_id,
        message=msg
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({"message": f"Employer verification updated to {status}"}), 200

from flask import Blueprint, request, jsonify
from models import db, Notification, Employer, User

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/', methods=['GET'])
def get_notifications():
    employer_id = request.args.get('employer_id')
    user_id = request.args.get('user_id')
    
    if not employer_id and not user_id:
        return jsonify({"error": "employer_id or user_id is required"}), 400
        
    query = Notification.query
    if employer_id:
        query = query.filter_by(employer_id=employer_id)
    if user_id:
        query = query.filter_by(user_id=user_id)
        
    notifications = query.order_by(Notification.created_at.desc()).all()
    
    return jsonify([{
        "id": n.id,
        "message": n.message,
        "is_read": n.is_read,
        "created_at": n.created_at.isoformat()
    } for n in notifications]), 200

@notifications_bp.route('/<int:notification_id>/read', methods=['PUT'])
def mark_read(notification_id):
    notification = Notification.query.get(notification_id)
    if not notification:
        return jsonify({"error": "Notification not found"}), 404
        
    notification.is_read = True
    db.session.commit()
    
    return jsonify({"message": "Notification marked as read"}), 200

@notifications_bp.route('/mark-all-read', methods=['PUT'])
def mark_all_read():
    data = request.get_json() or {}
    employer_id = data.get('employer_id')
    user_id = data.get('user_id')
    
    if not employer_id and not user_id:
        return jsonify({"error": "employer_id or user_id is required"}), 400
        
    query = Notification.query.filter_by(is_read=False)
    if employer_id:
        query = query.filter_by(employer_id=employer_id)
    if user_id:
        query = query.filter_by(user_id=user_id)
        
    notifications = query.all()
    for n in notifications:
        n.is_read = True
        
    db.session.commit()
    
    return jsonify({"message": "All notifications marked as read"}), 200

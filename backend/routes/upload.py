from flask import Blueprint, request, jsonify, current_app
import cloudinary
import cloudinary.uploader
import os

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/resume', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only PDF, DOC, and DOCX are allowed."}), 400
        
    # Check file size by seeking to end
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    if file_length > MAX_FILE_SIZE:
        return jsonify({"error": "File size exceeds 5MB limit."}), 400
        
    # Reset pointer before upload
    file.seek(0)
    
    # Configure cloudinary here inside route or init app, but since current_app is accessible:
    cloudinary.config(
        cloud_name=current_app.config.get('CLOUDINARY_CLOUD_NAME'),
        api_key=current_app.config.get('CLOUDINARY_API_KEY'),
        api_secret=current_app.config.get('CLOUDINARY_API_SECRET')
    )
    
    try:
        upload_result = cloudinary.uploader.upload(
            file,
            resource_type="auto",
            folder="trustjobs/resumes/"
        )
        return jsonify({
            "message": "File uploaded successfully",
            "url": upload_result.get("secure_url")
        }), 200
    except Exception as e:
        print("Upload failed:", e)
        return jsonify({"error": "Upload failed."}), 500

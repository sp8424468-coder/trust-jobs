from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db
from routes.auth import auth_bp
from routes.jobs import jobs_bp
from routes.users import users_bp
from routes.employer import employer_bp
from routes.notifications import notifications_bp
from routes.employer_jobs import employer_jobs_bp
from routes.verification import verification_bp
from routes.admin_auth import admin_auth_bp
from routes.admin import admin_bp
from routes.admin_management import admin_mgmt_bp
from routes.admin_trust import admin_trust_bp
from routes.upload import upload_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app)
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(jobs_bp, url_prefix='/api/jobs')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(employer_bp, url_prefix='/api/employer')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(employer_jobs_bp, url_prefix='/api/employer/jobs')
    app.register_blueprint(verification_bp, url_prefix='/api/verification')
    app.register_blueprint(admin_auth_bp, url_prefix='/api/admin/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(admin_mgmt_bp, url_prefix='/api/admin/management')
    app.register_blueprint(admin_trust_bp, url_prefix='/api/admin/trust')
    app.register_blueprint(upload_bp, url_prefix='/api/upload')

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy"})

    with app.app_context():
        # Create database tables for MVP (using SQLite if Postgres isn't configured yet)
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)

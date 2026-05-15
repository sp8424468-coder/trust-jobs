from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db
from routes.auth import auth_bp
from routes.jobs import jobs_bp
from routes.users import users_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app)
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(jobs_bp, url_prefix='/api/jobs')
    app.register_blueprint(users_bp, url_prefix='/api/users')

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

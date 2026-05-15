import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-for-mvp'
    # Use PostgreSQL if provided, otherwise fallback to SQLite for immediate local MVP testing
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///jobportal.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

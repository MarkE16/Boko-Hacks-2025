from flask import Flask
from extensions import db, mail  # Import db and mail from extensions.py
from routes.home import home_bp
from routes.hub import hub_bp
from routes.login import login_bp
from routes.register import register_bp
from routes.about import about_bp
from routes.apps import apps_bp
from routes.notes import notes_bp
from routes.admin import admin_bp, init_admin_db
from routes.files import files_bp
from routes.captcha import captcha_bp
from routes.retirement import retirement_bp
from routes.email import email_bp
from routes.news import news_bp  # Import the new news blueprint
from models.user import User
from models.note import Note
from models.admin import Admin
from models.file import File
from sqlalchemy import inspect
import os
# Import the logger to ensure it's initialized
from utils.logger import logger
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///boko_hacks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')  # Set default sender

app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # Set maximum file size to 10MB

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ensure logs directory exists
LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

db.init_app(app)
mail.init_app(app)

# Register Blueprints
app.register_blueprint(home_bp)
app.register_blueprint(hub_bp)
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(about_bp)
app.register_blueprint(apps_bp)
app.register_blueprint(notes_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(files_bp)
app.register_blueprint(captcha_bp)
app.register_blueprint(news_bp)
app.register_blueprint(retirement_bp)
app.register_blueprint(email_bp)

def setup_database():
    """Setup database and print debug info"""
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()

        if not existing_tables:
            print("No existing tables found. Creating new tables...")
            db.create_all()

            init_admin_db()
        else:
            print("Existing tables found:", existing_tables)

            db.create_all()
            print("Updated schema with any new tables")

        for table in ['users', 'notes', 'admin_credentials', 'files']:
            if table in inspector.get_table_names():
                print(f"\n{table.capitalize()} table columns:")
                for column in inspector.get_columns(table):
                    print(f"- {column['name']}: {column['type']}")
            else:
                print(f"\n{table} table does not exist!")

if __name__ == "__main__":
    setup_database()
    app.run(host='0.0.0.0', debug=True)

"""
The flask application package.
"""
import logging
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Set secret key from .env
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Initialize extensions
Session(app)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'

# Set up logging
logging.basicConfig(
    level=logging.INFO,  # Set logging level to INFO
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)
app.logger.setLevel(logging.INFO)

# Example log messages for testing (can be removed later)
app.logger.info("Flask app initialized successfully.")
app.logger.info("Logging is set up.")

import FlaskWebProject.views  # Import views after app initialization

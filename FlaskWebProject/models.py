from datetime import datetime
from FlaskWebProject import app, db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from azure.storage.blob import BlobServiceClient
import string
import random
from werkzeug.utils import secure_filename
from flask import flash

# Azure Blob Storage configuration
blob_container = app.config['BLOB_CONTAINER']
blob_service_client = BlobServiceClient.from_connection_string(app.config['BLOB_STORAGE_KEY'])
container_client = blob_service_client.get_container_client(blob_container)

def id_generator(size=32, chars=string.ascii_uppercase + string.digits):
    """
    Generate a random string of uppercase letters and digits.
    """
    return ''.join(random.choice(chars) for _ in range(size))

class User(UserMixin, db.Model):
    """
    User model for authentication.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """
        Hash and set the user's password.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Check if the provided password matches the stored hash.
        """
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    """
    Load a user by ID for Flask-Login.
    """
    return User.query.get(int(id))

class Post(db.Model):
    """
    Post model for storing article data.
    """
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    author = db.Column(db.String(75))
    body = db.Column(db.String(800))
    image_path = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Post {self.title}>'

    def save_changes(self, form, file, userId, new=False):
        """
        Save or update a post and handle image uploads to Azure Blob Storage.
        """
        self.title = form.title.data
        self.author = form.author.data
        self.body = form.body.data
        self.user_id = userId

        if file:
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1]
            random_filename = id_generator()
            filename = f"{random_filename}.{file_extension}"

            try:
                # Upload new image to Blob Storage
                blob_client = container_client.get_blob_client(filename)
                blob_client.upload_blob(file)

                # Delete old image if it exists
                if self.image_path:
                    old_blob_client = container_client.get_blob_client(self.image_path)
                    old_blob_client.delete_blob()

            except Exception as e:
                flash(f"An error occurred while uploading to Blob Storage: {str(e)}")
                app.logger.error(f"Blob Storage Error: {str(e)}")

            self.image_path = filename

        # Add new post or update existing one
        if new:
            db.session.add(self)
        db.session.commit()

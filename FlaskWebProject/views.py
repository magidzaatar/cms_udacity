"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, flash, redirect, request, session, url_for
from werkzeug.urls import url_parse
from config import Config
from FlaskWebProject import app, db
from FlaskWebProject.forms import LoginForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from FlaskWebProject.models import User, Post
import msal
import uuid
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

imageSourceUrl = 'https://' + app.config['BLOB_ACCOUNT'] + '.blob.core.windows.net/' + app.config['BLOB_CONTAINER'] + '/'

@app.route('/')
@app.route('/home')
@login_required
def home():
    """
    Home page displaying all posts.
    """
    user = User.query.filter_by(username=current_user.username).first_or_404()
    posts = Post.query.all()
    return render_template(
        'index.html',
        title='Home Page',
        posts=posts,
        imageSource=imageSourceUrl
    )

@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    """
    Create a new post.
    """
    form = PostForm(request.form)
    if form.validate_on_submit():
        post = Post()
        post.save_changes(form, request.files['image_path'], current_user.id, new=True)
        logger.info(f"New post created by user {current_user.username}.")
        return redirect(url_for('home'))
    return render_template(
        'post.html',
        title='Create Post',
        imageSource=imageSourceUrl,
        form=form
    )

@app.route('/post/<int:id>', methods=['GET', 'POST'])
@login_required
def post(id):
    """
    Edit an existing post.
    """
    post = Post.query.get(int(id))
    form = PostForm(formdata=request.form, obj=post)
    if form.validate_on_submit():
        post.save_changes(form, request.files['image_path'], current_user.id)
        logger.info(f"Post {id} updated by user {current_user.username}.")
        return redirect(url_for('home'))
    return render_template(
        'post.html',
        title='Edit Post',
        imageSource=imageSourceUrl,
        form=form
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login with username/password or Microsoft authentication.
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    
    # Handle username/password login
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            logger.warning(f"Unsuccessful login attempt with username: {form.username.data}")
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        logger.info(f"User {user.username} logged in successfully.")
        
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        
        return redirect(next_page)
    
    # Handle Microsoft authentication login
    session["state"] = str(uuid.uuid4())
    auth_url = _build_auth_url(scopes=Config.SCOPE, state=session["state"])
    
    return render_template('login.html', title='Sign In', form=form, auth_url=auth_url)

@app.route(Config.REDIRECT_PATH)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    """
    Handle Microsoft authentication callback.
    """
    if request.args.get('state') != session.get("state"):
        return redirect(url_for("home"))  # Invalid state
    
    if "error" in request.args:  # Authentication/Authorization failure
        logger.error(f"Microsoft authentication error: {request.args}")
        return render_template("auth_error.html", result=request.args)
    
    if request.args.get('code'):
        cache = _load_cache()
        msal_app = _build_msal_app(cache=cache)
        
        result = msal_app.acquire_token_by_authorization_code(
            request.args['code'],
            scopes=Config.SCOPE,
            redirect_uri=url_for('authorized', _external=True)
        )
        
        if "error" in result:
            logger.error(f"Token acquisition error: {result}")
            return render_template("auth_error.html", result=result)
        
        session["user"] = result.get("id_token_claims")
        
        # Log in as admin for this project (adjust as needed for multi-user support)
        user = User.query.filter_by(username="admin").first()
        login_user(user)
        
        _save_cache(cache)
        
        logger.info("Microsoft user authenticated successfully.")
    
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    """
    Log out the current user.
    """
    logout_user()
    
    if session.get("user"):  # Used MS Login
        session.clear()  # Clear session data
        
        # Logout from Microsoft tenant's web session
        return redirect(
            Config.AUTHORITY + "/oauth2/v2.0/logout" +
            "?post_logout_redirect_uri=" + url_for("login", _external=True)
        )
    
    logger.info("User logged out successfully.")
    
    return redirect(url_for('login'))

# Helper functions for MSAL integration

def _load_cache():
    """
    Load the token cache from MSAL.
    """
    cache = msal.SerializableTokenCache()
    
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    
    return cache

def _save_cache(cache):
    """
    Save the token cache to the session.
    """
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()

def _build_msal_app(cache=None, authority=None):
    """
    Build an MSAL ConfidentialClientApplication.
    """
    return msal.ConfidentialClientApplication(
        Config.CLIENT_ID,
        authority=authority or Config.AUTHORITY,
        client_credential=Config.CLIENT_SECRET,
        token_cache=cache
)

def _build_auth_url(authority=None, scopes=None, state=None):
    """
    Build the Microsoft authentication URL.
    """
    msal_app = _build_msal_app(authority=authority)
    
    return msal_app.get_authorization_request_url(
        scopes or [],
        state=state,
        redirect_uri=url_for('authorized', _external=True)
)


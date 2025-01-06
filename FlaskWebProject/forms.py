from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    """
    Form for user login.
    """
    username = StringField('Username', validators=[
        DataRequired(message="Username is required."),
        Length(max=64, message="Username must not exceed 64 characters.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required.")
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class PostForm(FlaskForm):
    """
    Form for creating or editing a post.
    """
    title = StringField('Title', validators=[
        DataRequired(message="Title is required."),
        Length(max=150, message="Title must not exceed 150 characters.")
    ], render_kw={"placeholder": "Enter the article title"})
    
    author = StringField('Author', validators=[
        DataRequired(message="Author name is required."),
        Length(max=75, message="Author name must not exceed 75 characters.")
    ], render_kw={"placeholder": "Enter the author's name"})
    
    body = TextAreaField('Body', validators=[
        DataRequired(message="Body text is required."),
        Length(max=800, message="Body text must not exceed 800 characters.")
    ], render_kw={"placeholder": "Write the article body here..."})
    
    image_path = FileField('Image', validators=[
        FileAllowed(['jpg', 'png'], 'Images only! (jpg, png)')
    ])
    
    submit = SubmitField('Save')

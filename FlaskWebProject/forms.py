from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    """
    Form for user login.
    """
    username = StringField('Username', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class PostForm(FlaskForm):
    """
    Form for creating or editing a post.
    """
    title = StringField('Title', validators=[DataRequired(), Length(max=150)])
    author = StringField('Author', validators=[DataRequired(), Length(max=75)])
    body = TextAreaField('Body', validators=[DataRequired(), Length(max=800)])
    image_path = FileField('Image', validators=[
        FileAllowed(['jpg', 'png'], 'Images only! (jpg, png)')
    ])
    submit = SubmitField('Save')

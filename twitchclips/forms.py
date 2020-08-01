from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_wtf.file import FileField, FileAllowed


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(max=120), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=30)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=120)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Password must match!')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=30)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=120)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=30)])
    email = StringField('Email', validators=[DataRequired(), Length(max=120), Email()])
    submit = SubmitField('Update')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    body = TextAreaField('Body', validators=[Length(max=3000)])
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    body = TextAreaField('Comment', validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField('Submit')


class EditPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    body = TextAreaField('Body', validators=[Length(max=3000)])
    submit = SubmitField('Submit')


class EditCommentForm(FlaskForm):
    body = TextAreaField('Comment', validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField('Submit')

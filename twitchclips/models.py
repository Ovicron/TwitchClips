from twitchclips import db, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    date_joined = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    posts = db.relationship('Post', backref='author',
                            lazy=True, passive_deletes=True)

    def __repr__(self):
        return f"User('{self.email}', '{self.username}', '{self.date_joined}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(300))
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.body}', '{self.link}', '{self.date_posted}')"

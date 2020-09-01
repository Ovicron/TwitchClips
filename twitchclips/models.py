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
    date_joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy=True, passive_deletes=True)
    comments = db.relationship('Comment', backref='author', lazy=True, passive_deletes=True)
    likes = db.relationship('PostLike', backref='author', foreign_keys='PostLike.user_id', lazy=True, passive_deletes=True)

    def __repr__(self):
        return f"User('{self.email}', '{self.username}', '{self.date_joined}')"

    def like_post(self, post):
        if not self.has_liked_post(post):
            like = PostLike(user_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(user_id=self.id, post_id=post.id).delete()

    def has_liked_post(self, post):
        return PostLike.query.filter(PostLike.user_id == self.id, PostLike.post_id == post.id).count() > 0


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(300))
    clip = db.Column(db.String(300))
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True, passive_deletes=True)
    likes = db.relationship('PostLike', backref='post', lazy=True, passive_deletes=True)

    def __repr__(self):
        return f"Post('{self.title}', '{self.body}', '{self.link}', '{self.date_posted}')"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    date_replied = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'))


class PostLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'))


class AverageViewers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    streamer = db.Column(db.String(25), nullable=False)
    viewers = db.Column(db.Integer, nullable=False)
    date_snapped = db.Column(db.DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return f"Data('{self.streamer}', '{self.viewers}', '{self.date_snapped}')"

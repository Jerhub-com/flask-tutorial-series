from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from scaffold import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    admin = db.Column(db.Boolean(), default=False)

    def __init__(self, username, email, password, admin):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.admin = admin

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(64), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=False)
    published = db.Column(db.Boolean(), default=False)

    def __init__(self, user, date, title, content, published):
        self.user = user
        self.date = date
        self.title = title
        self.content = content
        self.published = published

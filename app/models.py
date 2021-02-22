from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(), nullable=False)
    posts = db.relationship('Post', backref='author', lazy='dynamic',
                            cascade="all,delete",)
    comments = db.relationship('Comment', backref='author', lazy='dynamic',
                               cascade="all,delete",)

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password_hash(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                          nullable=False)
    title = db.Column(db.String(140), nullable=False)
    content = db.Column(db.String(), nullable=False)
    publication_datetime = db.Column(db.DateTime, index=True,
                                     default=datetime.utcnow)
    comments = db.relationship('Comment', backref='post', lazy='dynamic',
                               cascade="all,delete")

    def __repr__(self):
        return '<Post %r>' % self.title

    def serialized(self):
        return {
                'id': self.id,
                'author_id': self.author_id,
                'title': self.title,
                'content': self.content,
                'publication_datetime': self.publication_datetime
            }


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                          nullable=False)
    title = db.Column(db.String(140), nullable=False)
    content = db.Column(db.String(), nullable=False)
    publication_datetime = db.Column(db.DateTime, index=True,
                                     default=datetime.utcnow)

    def __repr__(self):
        return '<Comment %r>' % self.title

    def serialized(self):
        return {
                'id': self.id,
                'post_id': self.post_id,
                'author_id': self.author_id,
                'title': self.title,
                'content': self.content,
                'publication_datetime': self.publication_datetime
            }

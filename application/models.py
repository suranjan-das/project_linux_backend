from .database import db
from flask_security import UserMixin, RoleMixin
from flask_login import login_manager
from sqlalchemy.sql import func

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))    

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    public_id = db.Column(db.String)
    username = db.Column(db.String, unique=False)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False) 
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    decks = db.relationship('Deck', cascade='all, delete-orphan', backref='user', lazy='dynamic')

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class Deck(db.Model):
    __tablename__ = 'deck'
    d_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    deck_name = db.Column(db.String, nullable=False)
    deck_info = db.Column(db.String)
    time_created = db.Column(db.DateTime(timezone=True), default=func.current_timestamp())
    score = db.Column(db.Integer, default = 0)
    cards = db.relationship('Card', cascade='all, delete-orphan', backref='deck', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Card(db.Model):
    __tablename__ = 'card'
    c_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    front = db.Column(db.String, nullable=False)
    back = db.Column(db.String, nullable=False)
    score = db.Column(db.Integer, default = 0)
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.d_id'), nullable = False)
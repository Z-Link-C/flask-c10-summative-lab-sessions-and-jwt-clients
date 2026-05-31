from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from marshmallow import Schema, fields

from config import db, bcrypt

class User(db.Model):
    __tablename__ = 'users'
    id=db.Column(db.Integer,primary_key=True, nullable=False)
    username=db.Column(db.String,unique=True,nullable=False)
    _password_hash=db.Column(db.String)
    
    tasks=db.relationship('Tasks',back_populates='user', cascade='all, delete-orphan')

    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password hashes may not be viewed.')
    
    @password_hash.setter
    def password_hash(self,password):
        hash=bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash=hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash,password.encode('utf-8')
        )
    @validates('username')
    def val_uname(self, key, username):
        if not username:
            raise ValueError('Username must be present')
        return username
    
    def __repr__(self):
        return f'User: {self.username}, ID: {self.id}'
        
class Tasks(db.Model):
    __tablename__ = 'tasks'
    id=db.Column(db.Integer,primary_key=True, nullable=False)
    title=db.Column(db.String,nullable=False)
    details=db.Column(db.String,nullable=True)
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user=db.relationship('User',back_populates='tasks')
    @validates('title')
    def val_title(self,key,title):
        if not title:
            raise ValueError('Title must be present')
        return title
    
class UserSchema(Schema):
    id = fields.Integer()
    username = fields.String()

class TaskSchema(Schema):
    id = fields.Integer()
    title = fields.String()
    details = fields.String()
    completed = fields.Boolean()
    due_date = fields.String()
    user_id=fields.Integer()


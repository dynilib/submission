from flask_security import UserMixin, RoleMixin

from database import db

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    def __repr__(self):
        return self.name

    def __unicode__(self):
        return self.name

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(300), nullable=False)
    active = db.Column(db.Boolean(), nullable=False)
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    submissions = db.relationship('Submission', backref='user',
                            lazy='dynamic')
    
    def __repr__(self):
        return self.username

    def __unicode__(self):
        return self.username

class Competition(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    start_on = db.Column(db.DateTime())
    end_on = db.Column(db.DateTime())
    groundtruth = db.Column(db.String(500), nullable=False)
    submissions = db.relationship('Submission', backref='competition',
                            lazy='dynamic')
    
    def __repr__(self):
        return self.name

    def __unicode__(self):
        return self.name

class Submission(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'), nullable=False)
    filename = db.Column(db.String(500), nullable=False)
    submitted_on = db.Column(db.DateTime())
    comment = db.Column(db.Text)
    score = db.Column(db.Float)
    
    def __repr__(self):
        return "{}".format(self.id)

    def __unicode__(self):
        return "{}".format(self.id)

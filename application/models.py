from .database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    fullname = db.Column(db.String(), nullable=False)
    role = db.Column(db.String(), nullable=False, default='trekker') #Admin, Staff, Trekker/user
    status = db.Column(db.String(), default='pending') #pending, approve or blacklist
    joined_date = db.Column(db.DateTime(), default = datetime.utcnow)

    bookings = db.relationship('Booking', backref = 'user', lazy = True, cascade = 'all, delete-orphan')

class Trek(db.Model):
    __tablename__ = "treks"
    id = db.Column(db.Integer, primary_key=True)
    trekname = db.Column(db.String(), nullable = False)
    location = db.Column(db.String(), nullable = False)
    difficulty = db.Column(db.String(), nullable = False, default = 'Moderate')
    duration = db.Column(db.String(), nullable = False)
    slots = db.Column(db.Integer(), nullable = False)
    status = db.Column(db.String(), default = 'pending') #Pending, Approved, Open, Full, Closed, Completed
    start_date = db.Column(db.DateTime(), nullable = False)
    end_date = db.Column(db.DateTime(), nullable = False)
    description = db.Column(db.Text(), nullable = False)
    sname = db.Column(db.String(), nullable = False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff_profile.id'))

    bookings = db.relationship('Booking', backref='trek', lazy=True, cascade='all, delete-orphan')

class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable = False)
    booking_date = db.Column(db.DateTime(), default = datetime.utcnow)
    status = db.Column(db.String(), default = "Booked") #Booked, Cancelled, Completed, Approve,

class Staff(db.Model):
    __tablename__ = "staff_profile"
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique = True, nullable = False)
    phone = db.Column(db.String(), nullable = False)
    about = db.Column(db.Text(), nullable = False)
    location = db.Column(db.String(), nullable = False)
    experience = db.Column(db.String(), nullable = False)

    user = db.relationship('User', backref=db.backref('staff_profile', uselist=False))
    assigned_trek = db.relationship('Trek', backref = 'staff_profile', lazy = True)

class Trekker(db.Model):
    __tablename__ = "trekker_profile"
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique = True, nullable = False)
    phone = db.Column(db.String(), nullable = False)
    about = db.Column(db.Text(), nullable = False)
    location = db.Column(db.String(), nullable = False)
    trekking_experience = db.Column(db.String(), nullable = False)

    user = db.relationship('User', backref=db.backref('trekker_profile', uselist=False))
    


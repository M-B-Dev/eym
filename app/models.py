from datetime import datetime

from time import time

import json

import redis

import rq

from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin

from flask import current_app

from app import db, login


class Order(db.Model):
    """This keeps track of which buyers have bought which products."""

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    qty = db.Column(db.Integer)
    timestamp = db.Column(
        db.DateTime, 
        nullable=True, 
        index=True, 
        default=datetime.utcnow
        )

    def __repr__(self):
        return '<Order {}>'.format(self.id)


class About(db.Model):
    """This stores the about us text."""

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(1000))
    en_body = db.Column(db.String(1000), nullable=True)

    def __repr__(self):
        return '{}'.format(self.body)


class User(UserMixin, db.Model):
    """This store the data for each user."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    address = db.Column(db.String(140), nullable=True)
    address_1 = db.Column(db.String(140), nullable=True)
    address_2 = db.Column(db.String(140), nullable=True)
    address_3 = db.Column(db.String(140), nullable=True)
    city = db.Column(db.String(140), nullable=True)
    province = db.Column(db.String(140), nullable=True)
    post_code = db.Column(db.String(140), nullable=True)
    status = db.Column(db.String(20), nullable=True, default='user')
    orders = db.relationship('Order', backref='buyer', lazy='dynamic')
    tasks = db.relationship('Task', backref='user', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user',
                                    lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        """This hashes the user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """This checks the hashed password is correct."""
        return check_password_hash(self.password_hash, password)
    
    def user_query():
        """This helper function is for generating reports."""
        return User.query

    def launch_task(
            self, 
            name, 
            description, 
            users, 
            products, 
            to, 
            frm, 
            *args, 
            **kwargs
            ):
        """This places a job in a porcess queue."""
        rq_job = current_app.task_queue.enqueue(
            'app.tasks.' + name, 
            users, 
            products, 
            to, 
            frm,
            *args, 
            **kwargs
            )
        task = Task(
            id=rq_job.get_id(), 
            name=name, 
            description=description,
            user=self
            )
        db.session.add(task)
        return task

    def get_tasks_in_progress(self):
        """This returns every task for a given user."""
        return Task.query.filter_by(user=self, complete=False).all()

    def get_task_in_progress(self, name):
        """This returns the most recent incomplete task."""
        return Task.query.filter_by(name=name, user=self,
                                    complete=False).first()

    def add_notification(self, name, data):
        """This adds a notification to the Notification

        table for a specific user.
        """
        
        self.notifications.filter_by(name=name).delete()
        n = Notification(
            name=name, 
            payload_json=json.dumps(data), 
            user=self
            )
        db.session.add(n)
        return n


class Notification(db.Model):
    """The Notifications tabel."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        """This returns the notifcations as a JSON object."""
        return json.loads(str(self.payload_json))


class Task(db.Model):
    """This stores all processes."""
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        """This fecthes the current process of a user."""
        try:
            rq_job = rq.job.Job.fetch(
                self.id, 
                connection=current_app.redis
                )
        except (
            redis.exceptions.RedisError, 
            rq.exceptions.NoSuchJobError
            ):
            return None
        return rq_job

    def get_progress(self):
        """This establishes the prgress of a process."""
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100


class Product(db.Model):
    """This stores all product information."""
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(64))
    qty = db.Column(db.Integer)
    cat = db.Column(db.String(64))
    image_file = db.Column(
        db.String(20), 
        nullable=True, 
        default='default.jpg'
        )
    cart_image_file = db.Column(
        db.String(20), 
        nullable=True, 
        default='default.jpg'
        )
    back_image_file = db.Column(
        db.String(20), 
        nullable=True, 
        default='default.jpg'
        )
    price = db.Column(db.Integer)
    description = db.Column(db.String(128), nullable=True)
    en_description = db.Column(db.String(128), nullable=True)
    orders = db.relationship('Order', backref='product', lazy='dynamic')
        
    def __repr__(self):
        return '<Product {}>'.format(self.item)

    def product_query():
        """Ths helper returns a query function for select 

        field in the reports.
        """

        return Product.query


@login.user_loader
def load_user(id):
    """This returns the user as an object."""
    return User.query.get(int(id))
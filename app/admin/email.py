import os
from flask import render_template, flash, current_app
from flask_login import current_user
from flask_mail import Message
from threading import Thread
from app import mail


def send_email(user_order, name, messages, instructions, choices):
    """
    
    This generates an invoice HTML email with inline image 
    attachments.
    """
    
    msg = Message(subject=f"Order for {name}", 
        sender=current_app.config['ADMINS'], 
        recipients=[current_user.email], 
        bcc=["eymcreativa@gmail.com"]
        )
    msg.html = render_template(
        'checkout/order_email.html', 
        user_order=user_order, 
        name=name,
        messages=messages,
        instructions=instructions,
        choices=choices
        )
    for order in user_order:
        msg.attach(
            order[2],
            'image/gif',
            open(os.path.join(
                current_app.static_folder, 
                'img-cart/'+order[2]), 
                'rb'
                ).read(), 
            'inline', 
            headers=[['Content-ID','<'+ order[2]+'>'],]
            )
    msg.attach(
        'navbar3.png',
        'image/gif',
        open(os.path.join(
            current_app.static_folder, 
            'img/navbar3.png'), 'rb').read(), 
        'inline', 
        headers=[['Content-ID','<Myimage>'],]
        )
    Thread(
        target=send_async_email, 
        args=(current_app._get_current_object(), 
        msg
        )).start()


def feedback(message, email):
    """This generates a user feedback email."""
    msg = Message(
        subject=f"Feedback from {email}", 
        sender=current_app.config['ADMINS'][0], 
        recipients=["eymcreativa@gmail.com"]
        )
    msg.body = message
    flash('Your email has been sent.')
    Thread(
        target=send_async_email, 
        args=(current_app._get_current_object(), 
        msg
        )).start()


def send_async_email(app, msg):
    """This initiaiates a thread and sends the email."""
    with app.app_context():
        mail.send(msg)
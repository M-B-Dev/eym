import os

import stripe

import pdfkit

from flask import(
    render_template, 
    redirect, 
    url_for, 
    request, 
    session,
    make_response, 
    current_app
    )

from flask_login import current_user, login_required

from app.checkout import bp

from app.admin.email import feedback, send_email

from app.shop.shop_functions import empty_cart

from app.checkout.checkout_functions import *

from app.checkout.forms import NewOrderForm

from app.admin.forms import FeedbackForm


@bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """This loads the checkout page."""
    items = session['items']
    pub_key = current_app.config['PUB_KEY']
    stripe.api_key = current_app.config['STRIPE_API_KEY']
    if len(items) < 1:
        return redirect(url_for('shop.index'))
    emailForm = FeedbackForm()
    if emailForm.validate():
        feedback(emailForm.message.data)
        return redirect(url_for('checkout.checkout') + '#contacto')
    (user_order, 
    user_total, 
    its, is_item, 
    box_count, 
    messages, 
    box_choices, 
    is_box, 
    item_count) = finalising_order(items)
    error_message = set_messages(is_box, is_item, item_count, box_count)
    if error_message:
        return render_template(
            'checkout/checkout_error.html', 
            emailForm=emailForm, 
            items=session['items'], 
            total_products=session['total_products'], 
            total=session['total'], 
            title='Checkout', 
            error_message=error_message
            )
    form = populate_form(
        NewOrderForm(
            message_details=messages, box_choices=its
            ), 
            messages, 
            its, 
            box_choices
            )
    if request.method == 'GET':
        form = get_checkout_form(form)
    elif form.validate_on_submit():
        choices = check_items(box_choices, form.box_choices.data)      
        customer = stripe.Customer.create(
            email=request.form['stripeEmail'], 
            source=request.form['stripeToken']
            )
        charge = stripe.Charge.create(
            customer=customer.id,
            amount=user_total,
            currency='usd',
            description='The Product'
        )
        messages, instructions, name = post_checkout_form(form)
        add_order_to_db(user_order)
        send_email(
            user_order, 
            name, 
            messages, 
            instructions, 
            choices
            )
        empty_cart()
        set_Checkout_session_vars(
            user_order, 
            name, 
            messages, 
            instructions, 
            choices
            )
        return render_template(
            'checkout/invoice.html', 
            user_order=user_order, 
            name=name, 
            emailForm=emailForm, 
            items=session['items'], 
            total_products=0, 
            total=0,
            messages=messages, 
            instructions=instructions,
            choices=choices
            )
    return render_template(
        'checkout/checkout.html', 
        emailForm=emailForm, 
        items=session['items'], 
        total_products=session['total_products'], 
        total=session['total'], 
        title='Checkout', 
        form=form, 
        user_order=user_order, 
        pub_key=pub_key, 
        user_total=user_total,
        box_count = box_count
        )


@bp.route('/invoice_pdf')
@login_required
def invoice_pdf():
    """This generates a PDF of the user's order."""
    response = make_response(
        pdfkit.from_string(
            render_template(
                'checkout/invoice_pdf.html', 
                user_order=session['user_order'], 
                name=session['name'], 
                messages=session['messages'],
                instructions=session['instructions'],
                image=os.path.join(
                    current_app.root_path,
                    'static/img/navbar3.png'
                    ),
                choices=session['choices']
                ),
            False, 
            css=[
                os.path.join(
                    current_app.root_path,
                    "static/css/all.css"
                    ),
                os.path.join(
                    current_app.root_path, 
                    "static/css/bootstrap.min.css"
                    ), 
                os.path.join(
                    current_app.root_path,
                    "static/css/style.css"
                    )
                ]
            )
        )
    response.headers['Content-Type'] = 'application/pdf'
    response.headers[
        'Content-Disposition'
        ] = f'inline; filename={current_user.username}.pdf'
    pop_invoice_sessions()
    return response
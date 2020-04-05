import os

import stripe

from flask import(
    render_template, 
    redirect, 
    url_for, 
    request, 
    session, 
    jsonify, 
    make_response, 
    current_app
    )

from flask_login import current_user, login_required

from flask_babel import get_locale

from app.models import Product, Order, About

from app import db

from app.shop import bp

from app.admin.email import feedback, send_email

from app.shop.shop_functions import *

from app.checkout.forms import NewOrderForm

from app.admin.forms import FeedbackForm


@bp.route("/loadGifts")
def loadGifts():
    """This loads Themed boxes into javascript function 'scroller'."""
    return generic_loader(session['products']["Box"])


@bp.route("/loadItems")
def loadItems():
    """This loads items into javascript function 'scroller'."""
    return generic_loader(session['products']["Item"])


@bp.route("/loadBoxes")
def loadBoxes():
    """This loads empty boxes into javascript function 'scroller'."""    
    return generic_loader(session['products']["Empty Box"])


@bp.route('/index/clear')
def clear_session():
    """This empties all items from the cart."""
    empty_cart()
    return redirect(url_for("shop.index"))


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    """This loads main landing page and shop."""
    organise_products()
    form = FeedbackForm()
    initialize_session_vars()
    if request.method == 'GET' and current_user.is_authenticated:
        form.email.data = current_user.email
    if form.validate_on_submit():
        feedback(form.message.data, form.email.data)
        return redirect(url_for('shop.index')+'#contacto')
    return render_template(
        'shop/index.html',
        lang=str(get_locale()), 
        about=About.query.all(), 
        items=session['items'], 
        total_products=session['total_products'], 
        total=session['total'], 
        emailForm=form
        )


@bp.route("/add_item")
def add_item():
    """This adds item to the cart."""
    product = Product.query.get_or_404(request.args.get('product_id', type=int))
    items = session['items']
    if len(items) > 0:
        match = False
        for item in items:
            if item[3] == product.id:
                item[4] += 1
                add_to_session(item[0])
                match = True
                break
        if match == False:
            items = append_items(items, product)
            add_to_session(product.price)
    else:
        items = append_items(items, product)
        add_to_session(product.price)
    session['items'] = items
    return update_cart()


@bp.route("/remove_item")
def remove_item():
    """This removes item from the cart."""
    i = int(request.args.get('I', type=int))
    items = session['items']
    subtract_from_session(items[i][0])
    items[i][4] -= 1
    if items[i][4] == 0:
        del items[i]
    session['items'] = items
    return update_cart()


@bp.route("/update_cart")
def update_cart():
    """This triggers javascript to update cart without reload."""
    return jsonify(
        total=session['total'], 
        total_products=session['total_products'], 
        items=session['items']
        )
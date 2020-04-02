from datetime import datetime

from flask import(
    redirect, 
    url_for, 
    session,  
    flash
    )

from flask_babel import _

from flask_login import current_user

from app.models import Product, Order

from app import db


def return_message(
        key, item="_____", 
        product="", new_qty="", 
        item_count=None, 
        box_count=None
        ):
    """
    
    This selects a message to be outputted depending on the 
    arguments inputted.
    """

    message_strings = {
        "plural_stock_out": _("""Unfortunately there are not %(name)s 
            %(product)s's in stock. There is %(product)s 
            %(product)s available
            """, name=item[4], product=product, new_qty=new_qty),
        "singular_stock_out": _("""Unfortunately there are not %(name)s  
            %(product)s's in stock. There is %(product)s 
            %(product)s available
            """, name=item[4], product=product, new_qty=new_qty),
        "no_empty_box": _("""You have ordered one or more single 
            items without a box, please choose a 
            box or remove the item before proceeding
            """),
        "no_items": _("""You have ordered a single box without 
            any items, please choose an item 
            or remove the item before proceeding
            """),
        "insufficient_boxes": _("""You have ordered %(item_count)s items but 
            only %(box_count)s empty box. There is a maximum 
            of 3 items to an empty box. Please revise your 
            order by reducing the number of items 
            or adding an empty box to your order
            """, item_count=item_count, box_count=box_count),
        "insufficient_boxes_plural": _("""You have ordered %(item_count)s 
            items but only %(box_count)s empty boxes. There is a maximum of 
            3 items to an empty box. Please revise your order 
            by reducing the number of items or adding an empty 
            box to your order
            """, item_count=item_count, box_count=box_count),
        "more_boxes_than_items": _("""You have ordered more empty boxes 
            than items. There is a minimum of 1 item to an empty box. 
            Please revise your order by reducing the number of empty 
            boxes or adding an item to your order
            """),
        "too_many_items": _("""You can only put 3 items in a box. 
            Please reselect the items to place in each box. 
            Your card has not been charged
            """),
        'insufficient_items': _("""You are trying to send an empty box. 
            Please make sure that each box contains at 
            least one item. Your card has not been charged
            """)
        }
    return message_strings[key]


def finalising_order(items):
    """
    
    This checks to see if there is enough stock for each item in the 
    shopping basket. Then it allocates the correct message fields and 
    to each unique item in the basket.
    """

    its = []
    messages = []
    box_choices = []
    item_count = 0
    box_count = 0
    is_item = False
    is_box = False
    user_order = []
    user_total = 0
    for item in items:
        product = Product.query.get_or_404(item[3])
        if item[4] > product.qty:
            new_qty = item[4]-(item[4]-product.qty)
            if product.qty == 1:
                message = return_message(
                    "plural_stock_out", 
                    item, 
                    product.item, 
                    new_qty
                    )
            elif product.qty > 1:
                message = return_message(
                    "singular_stock_out", 
                    item, 
                    product.item, 
                    new_qty
                    )
            user_total += product.price * 100 * new_qty
        else:
            new_qty = item[4]
            user_total += product.price * 100 * item[4]
            message = None
        user_order.append(
            [product.item, 
            product.price, 
            product.image_file, 
            new_qty, message, 
            product.id, 
            product.cat]
            )
        (
        its, 
        is_item, 
        box_count, 
        messages, 
        box_choices, 
        is_box, 
        item_count
        ) = prepare_form_content(
            product, 
            new_qty, 
            its, 
            is_item, 
            box_count, 
            messages, 
            box_choices, 
            is_box, 
            item_count
            )
    return (
        user_order, 
        user_total, 
        its, is_item, 
        box_count, 
        messages, 
        box_choices, 
        is_box, 
        item_count
    )


def prepare_form_content(
        product, 
        new_qty, 
        its, 
        is_item, 
        box_count, 
        messages, 
        box_choices, 
        is_box, 
        item_count
        ):
    """
    
    this sets how many form fields and 
    select fields will be needed in the final order form.
    """

    if product.cat == "Item":
        for i in range(new_qty):
            if new_qty > 1:
                its.append({"name":product.item + f" {str(i+1)}"})
            else:
                its.append({"name":product.item})
        is_item = True
        item_count += new_qty
    elif product.cat == "Empty Box":
        for i in range(new_qty):
            if new_qty > 1:
                messages.append({"name":product.item + f" {str(i+1)}"})
                box_choices.append((
                    product.item + f" {str(i+1)}", 
                    product.item + f" {str(i+1)}"
                    ))
            else:
                messages.append({"name":product.item})
                box_choices.append((product.item, product.item))
        is_box = True
        box_count += new_qty
    else:
        for i in range(new_qty):
            if new_qty > 1:
                messages.append({"name":product.item+ f" {str(i+1)}"})
            else:
                messages.append({"name":product.item})
    return (
        its, 
        is_item, 
        box_count, 
        messages, 
        box_choices, 
        is_box, 
        item_count
        )


def set_messages(is_box, is_item, item_count, box_count):
    """
    
    This ensures that an appropriate number of empty boxes 
    (1 per 3 items) have been ordered for the number of items selected. 
    If not an apprpriate message is selected.
    """

    message = None
    if is_box != is_item:
        if is_box == False:
            message = return_message("no_empty_box")
        if is_item == False:
            message = return_message("no_items")
    if is_box == True:
        if item_count/box_count > 3:
            if box_count == 1:
                message = return_message(
                    "insufficient_boxes", 
                    item_count=item_count, 
                    box_count=box_count
                    )
            else:
                message = return_message(
                    "insufficient_boxes_plural", 
                    item_count=item_count, 
                    box_count=box_count
                    )
        elif box_count > item_count:
            message = return_message("more_boxes_than_items")
    return message


def check_items(box_choices, formData):
    """
    
    This checks that the user has put at least 1 item per box 
    and not over 3.
    """

    choices = []
    if len(box_choices) > 1:
        for choice in formData:
            choices.append(choice["box"])
        for choice in box_choices:
            if choices.count(choice[0]) > 3:
                flash(return_message("too_many_items"))
                return redirect(url_for("checkout.checkout"))
            elif choice[0] not in choices:
                flash(return_message('insufficient_items'))
                return redirect(url_for("checkout.checkout"))
    elif len(box_choices) == 1:
        for choice in formData:
            choices.append(box_choices[0][0])
    print(choices)
    return choices  


def populate_form(form, messages, its, box_choices):
    """
    
    This iterates over validated choices, 
    generating required form fields in the checkout form.
    """

    for i, sub in enumerate(form.message_details):
        sub.Gift_message.label = messages[i]["name"]
    for i, sub in enumerate(form.box_choices):
        sub.box.choices = box_choices
        sub.box.label = its[i]["name"]
    return form


def get_checkout_form(form):
    """
    
    This collects data from the database to populate 
    given form fields with placeholders.
    """
    
    form.name.data = current_user.username
    form.address_1.data = current_user.address_1
    form.address_2.data = current_user.address_2
    form.address_3.data = current_user.address_3
    form.city.data = current_user.city
    form.province.data = current_user.province
    form.postcode.data = current_user.post_code
    return form


def post_checkout_form(form):
    """
    
    This collects completed data, prepares some to 
    be stored in the database and locally stores others 
    ready for invoicing.
    """
    
    current_user.address_1 = form.address_1.data
    current_user.address_2 = form.address_2.data
    current_user.address_3 = form.address_3.data
    current_user.city = form.city.data
    current_user.province = form.province.data
    current_user.post_code = form.postcode.data
    messages = form.message_details.data
    instructions = form.instructions.data
    name = form.name.data
    return messages, instructions, name


def add_order_to_db(user_order):
    """This stores user order data to the database."""
    for item in user_order:
        product = Product.query.get_or_404(item[5])
        product.qty -= item[3]
        match = False
        for order in Order.query.filter_by(user_id=current_user.id):
            if order.product_id == int(item[5]):
                order.qty += item[3]
                order.timestamp = datetime.utcnow()
                match = True
                db.session.commit()
                break
        if match == False:
            order = Order(
                buyer=current_user, 
                product=product, 
                qty=1, 
                timestamp=datetime.utcnow()
                )
            db.session.add(order)
            db.session.commit()    


def set_Checkout_session_vars(
        user_order, 
        name, 
        messages, 
        instructions, 
        choices
        ):
    """This sets the session variables with order details."""
    session['user_order'] = user_order
    session['name'] = name
    session['messages'] = messages
    session['instructions'] = instructions
    session['choices'] = choices


def pop_invoice_sessions():
    """This clear all session order details."""
    session.pop('user_order')
    session.pop('name')
    session.pop('instructions')
    session.pop('messages')
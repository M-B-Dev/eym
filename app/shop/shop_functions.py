from flask import(
    request, 
    session, 
    jsonify, 
    make_response, 
    current_app
    )

from app.models import Product


def generic_loader(products):
    """
    
    This is triggered by the scroller JS function. It returns 
    a list of products.
    """

    if request.args:
        counter = int(request.args.get("c"))
        if counter == 0:
            res = make_response(
                jsonify(
                    products[
                        0 : current_app.config['PRODUCTS_IN_PAGE']
                        ]
                    ), 
                200
                )
        elif counter == len(products):
            res = make_response(jsonify({}), 200)
        else:
            res = make_response(
                jsonify(
                    products[
                        counter : counter + current_app.config[
                            'PRODUCTS_IN_PAGE'
                            ]
                        ]
                    ), 
                200
                )
    return res


def empty_cart():
    """This empties all session variables related to the cart."""
    session['items'] = []
    session['total'] = 0
    session['total_products'] = 0


def initialize_session_vars():
    """This sets all cart session variables to 0."""
    if 'total' not in session.keys():
        session['total_products'] = 0
        session['total'] = 0
    if 'items' not in session.keys():
        session['items'] = []


def organise_products():
    """
    
    This queries the product db and organises 
    the results into Item, box and empty box."""

    product_dict = {"Box": [], "Item": [], "Empty Box": []}
    for product in Product.query.all():
        if product.qty > 0:
            product_dict[product.cat].append(
                    [
                    product.id,
                    product.item,
                    product.cat,
                    product.image_file,
                    product.price,
                    product.qty,
                    product.description,
                    product.back_image_file
                    ]
                ) 
    session['products'] = product_dict


def add_to_session(total_addition):
    """
    
    This adds quantity and 
    price to the session variables.
    """

    session['total'] += total_addition
    session['total_products'] += 1


def subtract_from_session(total_subtraction):
    """
    
    This subtracts quantity and 
    price from the session variables.
    """
    
    session['total'] -= total_subtraction
    session['total_products'] -= 1


def append_items(items, product):
    """This appends the details of a product to items."""
    items.append([
    product.price, 
    product.item, 
    product.image_file, 
    product.id, 
    1
    ])
    return items
import os

import secrets

from PIL import Image, ImageOps

from flask_login import current_user

from flask_babel import _

from flask import current_app, flash, redirect, url_for

from app.models import Product

from app import db


def get_edit_product_form(form, product):
    """
    
    This sets the edit product form data from the values in the 
    database.
    """

    form.item.data = product.item
    form.qty.data = product.qty
    form.price.data = product.price
    form.cat.data = product.cat
    form.description.data = product.description
    form.image_file.data = product.image_file
    if form.en_description.data:
        form.en_description.data = product.en_description.data
    return form


def post_edit_product_form(form, product):
    """
    
    This takes the edit product form values 
    and saves them to the database
    """

    product.item = form.item.data
    if form.image_file.data:
        product.image_file = save_image(form.image_file.data, product.id, "front")
    if form.back_image_file.data:
        product.back_image_file = save_image(form.back_image_file.data, product.id, "back")
    product.qty = form.qty.data
    product.cat = form.cat.data
    product.description = form.description.data
    product.en_description = form.en_description.data
    product.price = form.price.data
    db.session.commit()
    flash(_('Your changes have been saved.'))
    return redirect(url_for('admin.edit_product', product_id=product.id))


def image_attributes(folder, width, height, picture_fn, form_image):
    """This resizes and saves an image."""
    image_path = os.path.join(current_app.root_path, folder, picture_fn)
    output_size = (width, height)
    i = Image.open(form_image)
    fit_and_resized_image = ImageOps.fit(i, output_size, Image.ANTIALIAS)
    fit_and_resized_image.save(image_path, quality=88)


def save_image(form_image, product_id=None, side=None):
    """
    
    This takes an image from a form, checks if it is for the front
    or back of the product, checks if it is new,
    then deletes and saves accordingly.
    """

    if product_id is not None:
        product = Product.query.get_or_404(product_id)
        if side == "front":
            delete_image(product.image_file)
        elif side == "back":
            delete_image(product.back_image_file)
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    picture_fn = random_hex + f_ext
    image_attributes('static/img', 800, 600, picture_fn, form_image)
    image_attributes('static/img-cart', 100, 100, picture_fn, form_image)
    return picture_fn


def delete_image(image_file):
    """This deletes an image"""
    if image_file != 'default.jpg':
        os.remove(current_app.root_path + '//static/img//' + image_file)
        os.remove(current_app.root_path + '//static/img-cart//' + image_file)


def check_category(image_data, cat_data, back_image_data):
    """
    
    This checks new product form data and 
    sets a default image file based on the category
    """
    
    if image_data:
        image_file = save_image(image_data, side="front")
    else:
        image_file = f"default {cat_data}.jpg"
    if back_image_data:
        back_image_file = save_image(back_image_data, side="back")
    else:
        back_image_file = f"default back {cat_data}.jpg"
    return image_file, back_image_file


def user_check():
    """checks if the user is admin or not"""
    if current_user.status == 'user' or current_user.email != "eymcreativa@gmail.com":
        return redirect(url_for('shop.index'))
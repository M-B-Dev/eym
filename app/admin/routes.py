from flask_login import login_required, current_user

from flask import( 
    render_template, 
    flash, 
    redirect, 
    url_for, 
    request, 
    session, 
    jsonify
    )

from app import db

from app.admin import bp

from app.admin.admin_functions import *

from app.admin.forms import(
    EditAboutForm, 
    NewProductForm, 
    ReportForm
    )

from app.models import( 
    User, 
    About, 
    Product, 
    Order,
    Notification
    )


@bp.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    """
    
    This renders the admin page. 
    It is only available to admin users.
    """

    user_check()
    about = About.query.filter_by().first()
    form = EditAboutForm()
    if form.validate_on_submit():
        about.body = form.body.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('admin.admin'))
    elif request.method == 'GET':
        form.body.data = about.body       
    return render_template(
        'admin/admin.html', 
        title='Admin', 
        form=form, 
        about=about, 
        products=Product.query.all(), 
        items=session['items'], 
        total_products=session['total_products'], 
        total=session['total'], 
        )


@bp.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    """
    
    This renders the products page. 
    It is only available to admin users.
    """

    user_check()
    return render_template(
        'admin/products.html', 
        title='Admin', 
        products=Product.query.all(), 
        items=session['items'], 
        total_products=session['total_products'], 
        total=session['total'], 
        )


@bp.route('/new_product', methods=['GET', 'POST'])
@login_required
def new_product():
    """
    
    This allows a new product to be entered into the database.
    It is only available to admin users.
    """

    user_check()
    form = NewProductForm()
    if form.validate_on_submit():
        image_file, back_image_file = check_category(
            form.image_file.data, 
            form.cat.data, 
            form.back_image_file.data
            )
        product = Product(
            item=form.item.data, 
            image_file=image_file,
            back_image_file=back_image_file,  
            cart_image_file=image_file, 
            qty=form.qty.data, 
            description=form.description.data, 
            cat=form.cat.data, 
            price=form.price.data
            )
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('admin.products'))
    return render_template(
        'admin/new_product.html', 
        title='New Product', 
        form=form, items=session['items'], 
        total_products=session['total_products'], 
        total=session['total']
        )


@bp.route("/product<int:product_id>", methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """
    
    This allows a product to be edited
    It is only available to admin users.
    """

    user_check()
    form = NewProductForm()
    if request.method == 'GET':
        form = get_edit_product_form(form, Product.query.get_or_404(product_id))
    elif form.validate_on_submit():
        post_edit_product_form(form, Product.query.get_or_404(product_id))
    return render_template(
        'admin/edit_product.html', 
        title='Edit Product', 
        form=form, 
        product=Product.query.get_or_404(product_id), 
        product_id=product_id, 
        items=session['items'], 
        total_products=session['total_products'], 
        total=session['total']
        )


@bp.route("/product/<int:product_id>/delete", methods=['GET','POST'])
@login_required
def delete_product(product_id):
    """
    
    This allows a product to be deleted. 
    It is only available to admin users.
    """ 

    user_check()
    product = Product.query.get_or_404(product_id)
    delete_image(product.image_file)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin.admin'))


@bp.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    """
    
    This renders the users page.
    It is only available to admin users.
    """

    user_check()
    return render_template(
        'admin/users.html', 
        title='Users', 
        users=User.query.all(), 
        items=session['items'], 
        total_products=session['total_products'], 
        total=session['total']
        )


@bp.route('/admin/users/<int:user_id>', methods=['GET', 'POST'])
@login_required
def turn_admin_or_user(user_id):
    """
    
    This switches a user from being admin to being a admin and vice versa. 
    It is only available to admin users.
    """

    user_check()
    user = User.query.get_or_404(user_id)
    if user.status == "admin":
        user.status = "user"
    else:
        user.status = "admin"
    db.session.commit()
    flash('Your changes have been saved.')
    return redirect(url_for('admin.users'))


@bp.route('/reports', methods=['GET', 'POST'])
@login_required
def reports():
    """
    
    This renders the reports page.
    It is only available to admin users.
    """

    user_check()
    form = ReportForm()
    if form.validate_on_submit():
        if current_user.get_task_in_progress('export_report'):
            print(current_user.get_task_in_progress('export_report'))
            flash('An export task is currently in progress')
        if True:
            current_user.launch_task(
                'export_report', 
                'Exporting reports...', 
                form.users.data, 
                form.products.data, 
                form.to.data, 
                form.frm.data
                )
            db.session.commit()
        return redirect(url_for('admin.reports'))
    return render_template(
        'admin/reports.html', 
        title='Admin', 
        form=form,
        items=session['items'], 
        total_products=session['total_products'], 
        total=session['total']
        )


@bp.route('/notifications')
@login_required
def notifications():
    """
    
    This collects any notifications for the current user.
    It is only available to admin users.
    """

    user_check()
    notifications = current_user.notifications.filter(
        Notification.timestamp > request.args.get('since', 0.0, type=float)).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])


@bp.route("/user_products<int:user_id>", methods=['GET','POST'])
@login_required
def user_products(user_id):
    """
    
    This renders a page of products that the user has bought.
    It is only available to admin users.
    """

    user_check()
    return render_template(
        'admin/user_products.html', 
        orders=Order.query.filter_by(user_id=user_id), 
        user=User.query.filter_by(id=user_id).first_or_404(), 
        items=session['items'], 
        total_products=session['total_products'], 
        total=session['total']
        )


@bp.route("/product_users<int:product_id>", methods=['GET','POST'])
@login_required
def product_users(product_id):
    """
    
    This renders a page of users who bought a particular product.
    It is only available to admin users.
    """
    
    user_check()
    return render_template(
        'admin/product_users.html', 
        orders=Order.query.filter_by(product_id=product_id), 
        product=Product.query.filter_by(id=product_id).first_or_404(), 
        items=session['items'], 
        total_products=session['total_products'], 
        total=session['total']
        )
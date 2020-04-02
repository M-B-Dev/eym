from flask_wtf import FlaskForm

from wtforms import(
    StringField, 
    IntegerField, 
    FloatField, 
    TextAreaField, 
    SubmitField, 
    DateField, 
    SelectField
    )

from wtforms.fields.html5 import EmailField

from wtforms.validators import DataRequired, InputRequired, Optional, Email

from flask_wtf.file import FileAllowed, FileField

from wtforms.ext.sqlalchemy.fields import(
    QuerySelectMultipleField, 
    QuerySelectField
    )

from app.models import Product, User


class FeedbackForm(FlaskForm):
    """Feedback email form."""
    message = TextAreaField(validators=[DataRequired()])
    email = EmailField("Email", [
        InputRequired("Please enter your email address."), 
        Email("Please enter your email address.")
        ])
    submit = SubmitField('Send')


class ReportForm(FlaskForm):
    """Report generation form."""
    users = QuerySelectMultipleField(
        query_factory=User.user_query, 
        get_label="email"
        )
    products = QuerySelectMultipleField(
        query_factory=Product.product_query, 
        get_label="item"
        )
    frm = DateField('From', validators=[Optional()])
    to = DateField('To', validators=[Optional()])
    submit = SubmitField('Generate')


class EditAboutForm(FlaskForm):
    """About section form."""
    body = TextAreaField()
    submit = SubmitField('Edit')


class NewProductForm(FlaskForm):
    """New product form."""
    item = StringField('item name', validators=[DataRequired()])
    qty = IntegerField('Quantity', validators=[InputRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    cat = SelectField(
        'Category', 
        validators=[DataRequired()], 
        choices=[("Empty Box", "Empty Box"), ("Item", "Item"), ("Box", "Box")]
        )
    description = StringField('Description')
    image_file = FileField(
        'Product Image', 
        validators=[FileAllowed(['jpg', 'png', 'jpeg'])]
        )
    back_image_file = FileField(
        'Description Image', 
        validators=[FileAllowed(['jpg', 'png', 'jpeg'])]
        )
    submit = SubmitField('Submit')
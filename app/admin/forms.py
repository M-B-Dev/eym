from flask_wtf import FlaskForm

from flask_babel import lazy_gettext as _l

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
    message = TextAreaField(validators=[DataRequired(_l("Please enter a message"))])
    email = EmailField(_l("Email"), [
        InputRequired(_l("Please enter your email address.")), 
        Email(_l("Please enter your email address."))
        ])
    submit = SubmitField(_l('Send'))


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
    frm = DateField(_l('From'), validators=[Optional()])
    to = DateField(_l('To'), validators=[Optional()])
    submit = SubmitField('Generate')


class EditAboutForm(FlaskForm):
    """About section form."""
    body = TextAreaField()
    en_body = TextAreaField()
    submit = SubmitField(_l('Edit'))


class NewProductForm(FlaskForm):
    """New product form."""
    item = StringField(_l('item name'), validators=[DataRequired(_l("Please enter the product name"))])
    qty = IntegerField(_l('Quantity'), validators=[InputRequired(_l("Please enter the quantity of the product as a whole number"))])
    price = FloatField(_l('Price'), validators=[DataRequired(_l("Please enter the price of the product"))])
    cat = SelectField(
        _l('Category'), 
        validators=[DataRequired(_l("Please choose either box, item or empty box"))], 
        choices=[("Empty Box", "Empty Box"), ("Item", "Item"), ("Box", "Box")]
        )
    description = StringField(_l('Description'), validators=[DataRequired(_l("Please enter a description in Spanish"))])
    en_description = StringField(_l('English Description'), validators=[DataRequired(_l("Please enter a description in English"))])
    image_file = FileField(
        _l('Product Image'), 
        validators=[FileAllowed(['jpg', 'png', 'jpeg'])]
        )
    back_image_file = FileField(
        _l('Description Image'), 
        validators=[FileAllowed(['jpg', 'png', 'jpeg'])]
        )
    submit = SubmitField(_l('Submit'))
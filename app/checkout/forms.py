from flask_wtf import FlaskForm

from flask_babel import lazy_gettext as _l

from wtforms import(
    StringField, 
    FloatField, 
    SubmitField, 
    TextAreaField, 
    FieldList, 
    SelectField, 
    FormField
)

from wtforms.validators import DataRequired, Optional

class MessageForm(FlaskForm):
    """
    
    This form allows for a gift message to be entered by the 
    user.
    """

    Gift_message = TextAreaField(validators=[DataRequired(_l("Please provide a message for this gift box. Your card has not been charged"))])

class BoxForm(FlaskForm):
    """
    
    This form allows the user to select which box an item will be 
    placed in.
    """

    box = SelectField()

class NewOrderForm(FlaskForm):
    """
    
    This form is the main checkout page form where users 
    enter all of their order details.
    """
    
    name = StringField(_l('Name'), validators=[DataRequired(_l("Please provide a recipient name. Your card has not been charged"))])
    address_1 = StringField(
        _l('Address Line 1'), 
        validators=[DataRequired(_l("Please provide the first line of the address. Your card has not been charged"))]
        )
    address_2 = StringField(_l('Adress Line 2'))
    address_3 = StringField(_l('Adress Line 3'))
    city = StringField(_l('City'), validators=[DataRequired(_l("Please provide a town or city. Your card has not been charged"))])
    province = StringField(_l('State'), validators=[DataRequired(_l("Please provide the province, county or state. Your card has not been charged"))])
    postcode = StringField(
        _l('Postal/Zip Code'), 
        validators=[DataRequired(_l("Please provide the postal/zip. Your card has not been charged"))]
        )
    instructions = TextAreaField(_l('Instructions'), validators=[Optional()])
    submit = SubmitField(_l('Pay'))
    message_details = FieldList(FormField(MessageForm))
    box_choices = FieldList(FormField(BoxForm))
    total = FloatField()
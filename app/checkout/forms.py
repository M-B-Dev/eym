from flask_wtf import FlaskForm

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

    Gift_message = TextAreaField(validators=[DataRequired()])

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
    
    name = StringField('Name', validators=[DataRequired()])
    address_1 = StringField(
        'Address Line 1', 
        validators=[DataRequired()]
        )
    address_2 = StringField('Adress Line 2')
    address_3 = StringField('Adress Line 3')
    city = StringField('City', validators=[DataRequired()])
    province = StringField('State', validators=[DataRequired()])
    postcode = StringField(
        'Postal/Zip Code', 
        validators=[DataRequired()]
        )
    instructions = TextAreaField('Instructions', validators=[Optional()])
    submit = SubmitField('Pay')
    message_details = FieldList(FormField(MessageForm))
    box_choices = FieldList(FormField(BoxForm))
    total = FloatField()


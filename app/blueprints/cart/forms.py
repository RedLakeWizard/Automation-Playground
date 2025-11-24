from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class CartAddForm(FlaskForm):
    quantity = IntegerField("Quantity", validators=[DataRequired(), NumberRange(min=1)], default=1)
    submit = SubmitField("Add to cart")


class CartUpdateForm(FlaskForm):
    quantity = IntegerField("Quantity", validators=[DataRequired(), NumberRange(min=0)], default=1)
    submit = SubmitField("Update")
    next = HiddenField()

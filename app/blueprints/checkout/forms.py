from flask_wtf import FlaskForm
from wtforms import SubmitField


class CheckoutPlaceholderForm(FlaskForm):
    submit = SubmitField("Proceed")

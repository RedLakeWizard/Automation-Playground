from decimal import Decimal

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import BooleanField, DecimalField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class AdminProductForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=200)])
    price = DecimalField(
        "Price",
        validators=[DataRequired(), NumberRange(min=0)],
        places=2,
        rounding=None,
        default=0,
    )
    compare_price = DecimalField(
        "Compare at Price",
        validators=[NumberRange(min=0)],
        places=2,
        rounding=None,
        default=0,
    )
    sku = StringField("SKU", validators=[DataRequired(), Length(min=2, max=64)])
    quantity = IntegerField("Quantity", validators=[DataRequired(), NumberRange(min=0)], default=10)
    is_active = BooleanField("Available", default=True)
    image = FileField("Image", validators=[FileAllowed(["jpg", "jpeg", "png", "gif"])])
    submit = SubmitField("Save")

    @property
    def price_cents(self) -> int:
        if self.price.data is None:
            return 0
        return int(Decimal(self.price.data) * Decimal(100))

    @property
    def compare_price_cents(self) -> int:
        if self.compare_price.data is None:
            return 0
        return int(Decimal(self.compare_price.data) * Decimal(100))

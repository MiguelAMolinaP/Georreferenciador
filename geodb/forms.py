from flask_wtf import FlaskForm
from wtforms import SubmitField

class GeorreferenciarForm(FlaskForm):
    submit = SubmitField(label= 'Georreferenciar')


class GeorreferenciarFormGoogle(FlaskForm):
    submit = SubmitField(label= 'Usar Google Maps')


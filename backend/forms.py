from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField

from parser.funcs import get_category_form_attributes


CategoryForm = type('CategoryForm', (FlaskForm, ),
                    {**get_category_form_attributes(), 'submit': SubmitField('Применить')})

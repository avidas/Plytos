import models
from flask.ext.mongoengine.wtf import model_form
from wtforms.fields import *
from flask.ext.mongoengine.wtf.orm import validators

user_form = model_form(models.User, exclude=['password'])

# Login form will provide a Password field (WTForm form field)
class LoginForm(user_form):
    username = TextField('Username', validators=[validators.Required()])
    password = PasswordField('Password', validators=[validators.Required()])
    remember_me = BooleanField('remember_me', default = False)

# Signup Form created from user_form
class RegisterForm(user_form):
    username = TextField('Username', validators=[validators.Required(), validators.Length(min=5, max=25)])
    password = PasswordField('Password', validators=[validators.Required(), validators.Length(min=6, max=40)])
    confirm  = PasswordField('Repeat Password', validators=[validators.Required(), validators.EqualTo('password', message='Passwords must match')])

# For resetting password
class ForgotForm(user_form):
    pass

class ResetPassForm(user_form):
	password = PasswordField('Password', validators=[validators.Required(), validators.Length(min=6, max=40)])
	confirm  = PasswordField('Repeat Password', validators=[validators.Required(), validators.EqualTo('password', message='Passwords must match')])
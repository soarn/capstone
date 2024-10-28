from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, HiddenField, SubmitField, PasswordField, EmailField, BooleanField, FloatField, SelectField
from wtforms.validators import DataRequired, NumberRange, Email, Length, Optional

# WEB: Transaction Form
class TransactionForm(FlaskForm):
    stock_id = HiddenField("Stock ID", validators=[DataRequired()], default="")
    stock_symbol = HiddenField("Stock Symbol", validators=[DataRequired()], default="")
    quantity = IntegerField("Quantity", validators=[DataRequired(), NumberRange(min=1, message="Quantity must be greater than 0")])

# WEB: Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit   = SubmitField('Login')

# WEB: Register Form
class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name  = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    username   = StringField('Username', validators=[DataRequired(), Length(max=80)])
    email      = EmailField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password   = PasswordField('Password', validators=[DataRequired()])
    submit     = SubmitField('Register')

# PROFILE: Update Account Form
class UpdateAccountForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name  = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    username   = StringField('Username', validators=[DataRequired(), Length(max=80)])
    email      = EmailField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password   = PasswordField('New Password', validators=[Optional()])
    submit     = SubmitField('Update Account')

    # TODO: #26 Combine RegisterForm and UpdateAccountForm into a single form

# PROFILE: Update Profile Form
class UpdateProfileForm(FlaskForm):
    username         = StringField('Username', validators=[DataRequired(), Length(max=80)])
    email            = EmailField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password         = PasswordField('New Password', validators=[Optional()])
    theme            = SelectField('Theme', choices=[], validators=[Optional()])
    pagination       = IntegerField('Pagination', validators=[DataRequired(), NumberRange(min=1)], default=10)
    notifications    = BooleanField('Receive Email Notifications')
    data_sharing     = BooleanField('Allow Data Sharing')
    confetti_enabled = BooleanField('Enable Confetti')
    submit           = SubmitField('Update Profile')

# ADMIN: Update Stock Form
class UpdateStockForm(FlaskForm):
    stock_id               = SelectField('Select Stock', validators=[DataRequired()], coerce=int)
    new_price              = FloatField('New Price', validators=[DataRequired()])
    is_manual              = BooleanField('Set Price Manually')
    fluctuation_multiplier = FloatField('Fluctuation Multiplier', validators=[DataRequired(), NumberRange(min=0.01)], default=1.0)
    submit                 = SubmitField('Update Stock')

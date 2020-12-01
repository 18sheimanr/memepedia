from flask import Flask, render_template, request, redirect
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///memepedia.db'

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
migrate = Migrate(app, db)

application = app

#TODO: Validators
class loginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password')
    submit = SubmitField('Sign In')

class signUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password')
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Sign Up')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    user = "Stranger"
    return render_template('home.html', user=user)

@app.route('/profile')
def profile():
    return render_template('profile.html', username="User123", joinDate="11/11/2020")

@app.route('/signIn', methods=['GET', 'POST'])
def signIn():
    form = loginForm()
    if form.validate_on_submit():
        new_name = request.form['username']
        try:
            #database commit
            return redirect('/home')
        except Exception:
            return "Could not log in or register!"
    else:
        return render_template('signIn.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signUp():
    form = signUpForm()
    if form.validate_on_submit():
        new_name = request.form['username']
        try:
            #database commit
            return redirect('/')
        except Exception:
            return "Could not log in or register!"
    else:
        return render_template('signup.html', form=form)

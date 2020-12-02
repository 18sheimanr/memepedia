import os
from flask.helpers import url_for
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from flask import Flask, render_template, request, redirect, flash, send_from_directory
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# Directory for uploading and storing all memes.
UPLOAD_FOLDER = basedir+"/static/memes"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
migrate = Migrate(app, db)

application = app

# TODO: Validators

# Checks if file is allowed to be uploaded.


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database models.

# Meme model. Has a primary key and variable for its filename.


class Meme(db.Model):
    _tablename_ = 'meme'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return '<Meme %r>' % self.id


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
    # Code for uploading pics to database and filesystem.
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        # Handling if user does not select file
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # Uploads to filesystem.
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Create meme with path and add to database
            name = filename
            meme = Meme(name=name)
            db.session.add(meme)
            db.session.commit()
            return redirect(url_for('memebase'))

    return render_template('index.html')

# Temporary route for testing. Fetches all memes currently in database.
@app.route('/memes', methods=['GET'])
def memebase():
    memes = Meme.query.all()
    return render_template('sample.html', memes=memes)

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


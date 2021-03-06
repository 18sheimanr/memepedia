import os
import random
from datetime import date
from flask.helpers import url_for
from werkzeug.utils import secure_filename
from wtforms.fields.simple import HiddenField
from flask_migrate import Migrate
from flask import Flask, render_template, request, redirect, flash, send_from_directory, jsonify
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, HiddenField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# Directory for uploading and storing all memes.
UPLOAD_FOLDER = basedir+"/static/memes"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
migrate = Migrate(app, db, render_as_batch=True)

login_manager = LoginManager()
login_manager.session_protection = 'strong'
# login_manager.login_view = 'auth.login'

login_manager.init_app(app)

application = app

# TODO: Validators

# Checks if file is allowed to be uploaded.
db.create_all()

# METHODS


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def delete_missing_memes():
    memes = Meme.query.all()
    for m in memes:
        if not os.path.exists('static/memes/'+m.name):
            try:
                print('static/memes/'+m.name)
                db.session.delete(m)
                db.session.commit()
                print("Deleted missing meme path.")
            except:
                print("Error")

# Create


def upload(request):
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
            meme = Meme(name=filename, uploader_id=current_user.id)
            db.session.add(meme)
            db.session.commit()
            return redirect(url_for('.home'))

    # MODELS


class User(UserMixin, db.Model):
    _tablename_ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False,
                         unique=True, index=True)
    joinDate = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # one-to-many relationship
    #
    memes = db.relationship('Meme', backref='uploader')

    def __repr__(self):
        return '<User %r>' % self.username


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Meme model. Has a primary key and variable for its filename.


class Meme(db.Model):
    _tablename_ = 'meme'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False, unique=True)
    likes = db.Column(db.Integer, default=0)
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Meme %r>' % self.id


class loginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password')
    submit = SubmitField('Sign In')


class signUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired(), EqualTo('confirm_password', message='Passwords must match.')])
    confirm_password = PasswordField(
        'Confirm Password', validators=[DataRequired()])

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

    submit = SubmitField('Sign Up')


# ROUTES
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect(url_for('.index'))


@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('.home'))
    memes = Meme.query.all()
    random.shuffle(memes)
    if len(memes) < 3:
        meme1 = Meme(name='img1.jpg')
        meme2 = Meme(name='img2.jpg')
        meme3 = Meme(name='img3.jpg')
        memes = [meme1, meme2, meme3]
    return render_template('index.html', memes=memes[-3:])


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    delete_missing_memes()
    upload(request)
    if len(request.args) == 0:
        if not current_user.is_authenticated:
            return redirect(url_for('.signUp'))
        else:
            return render_template('profile.html', memes=current_user.memes, user=current_user)
    user=User.query.filter_by(id=request.args.get('id'))[0]
    names=[user.username for x in range(0, len(user.memes))]
    return render_template('profile.html', memes=user.memes, user=user, uploader_names=names)


# Delete
@app.route('/delete', methods=['POST'])
def delete():
    id = int(request.form['meme_to_delete'])
    meme = Meme.query.filter_by(id=id).first()
    filename = meme.name
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    db.session.delete(meme)
    db.session.commit()
    return redirect(request.referrer)

# Update
@app.route('/like', methods=['POST'])
def like():
    try:
        meme_id = request.form['id']
        meme = Meme.query.filter_by(id=meme_id).first()
        meme.likes = meme.likes+1
        db.session.add(meme)
        db.session.commit()
        return jsonify(
            message="there are now {} likes.".format(meme.likes),
            category="success",
            status=200
        )
    except:
        return jsonify(
            message="Could not like.",
            status=400
        )



@app.route('/signIn', methods=['GET', 'POST'])
def signIn():
    form = loginForm()
    if form.validate_on_submit():
        name = request.form['username']
        user = User.query.filter_by(username=name).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('.home'))
        else:
            flash('Invalid username or password.')
            return render_template('signIn.html', form=form)
    else:
        return render_template('signIn.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signUp():
    form = signUpForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    password=form.password.data,
                    joinDate=date.today().strftime("%B %d, %Y"))
        try:
            db.session.add(user)
            db.session.commit()
            flash('You can now login.')
            return redirect(url_for('.signIn'))
        except Exception:
            return "Could not register!"
    else:
        return render_template('signup.html', form=form)


@app.route('/home', methods=['GET', 'POST'])
# @login_required
def home():
    memes = Meme.query.all()
    random.shuffle(memes)
    uploader_names=[]
    for i in range(0, len(memes)):
        uploader_name = User.query.filter_by(id=memes[i].uploader_id)[0].username
        uploader_names.append(uploader_name)
    return render_template('home.html', memes=memes, uploader_names=uploader_names)

@app.route('/popup', methods=['POST'])
def popup():
    meme_id = request.form['id']
    meme = Meme.query.filter_by(id=meme_id)[0]
    uploader_name = User.query.filter_by(id=meme.uploader_id)[0].username
    return render_template('memePopUp.html', meme=meme, uploader_name=uploader_name)
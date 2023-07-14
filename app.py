import datetime
from docxtpl import DocxTemplate
from pathlib import Path
from flask import Flask, render_template, redirect, url_for
from flask import request
# import request
import docx

import os
from werkzeug.utils import secure_filename

# login
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt



app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static/uploads/')
# for connecting the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# for creating a session cookie, we need a secret
app.config['SECRET_KEY'] = 'hi'

# for logging in user
login_manager = LoginManager() #flask login
login_manager.init_app(app)
login_manager.login_view = 'login'
# used to load/reload objects from the stored session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# creating user db
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    # hashed password is longer..
    password  = db.Column(db.String(80), nullable=False)
# after writing this, go to terminal, import db variable, then give db.create_all() to create all tables.

# user validation when he inputs username and passwd(register page)
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4,max=20)], render_kw={'placeholder':'Username'})
    password = PasswordField(validators=[InputRequired(), Length(min=4,max=20)], render_kw={'placeholder':'Password'})
    submit = SubmitField("Register")

    # checking for existing user
    def validate_username(self, username):
        existing_username = User.query.filter_by(username=username.data).first()
        if existing_username:
            raise ValidationError("Username already exists")

# for login page
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4,max=20)], render_kw={'placeholder':'Username'})
    password = PasswordField(validators=[InputRequired(), Length(min=4,max=20)], render_kw={'placeholder':'Password'})
    submit = SubmitField("Login")


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods = ['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('forms'))



    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods = ['GET','POST'])
def register():
    form = RegisterForm()
    try:
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    except:
        print('Wrong')

    return render_template('register.html', form=form)


def populate2(filename,context):
    # filename='vendor-contract'
    document_path = Path(__file__).parent / ('static/uploads/' + filename + '.docx')
    doc = DocxTemplate(document_path)

    context = context
    # return context
    # num = 2

    doc.render(context)
    doc.save(Path(__file__).parent / f"{filename[0:2]}-contract.docx")
    # print("Hello")





# to upload a file and filename
@app.route('/forms')
@login_required
def forms():
    return render_template('forms.html')

filenames = []
filename = ''
# a post request to handle the file upload
@app.route('/uploader', methods=['GET','POST'])
@login_required
def uploader():
    if request.method == 'POST':
        f = request.files['file1']
        filename = request.form.get("filename")
        f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
        print(filename)
        if filename in filenames:
            return 'already exists'
        else:
            filenames.append(filename)
            return filename

#to get the  inputs from user for the extracted variables
@app.route('/input')
@login_required
def input():
    print(filenames)
    return render_template('input.html',filenames=filenames)

@app.route('/inputypes', methods = ['GET','POST'])
@login_required
def inputypes():
    filename = request.form.get('filename')
    print(filename)


    doc = docx.Document('static/uploads/' + filename + '.docx')
 


    l=[]

    for p in doc.paragraphs:
        a=p.text
        
        s=''
        for i in range(len(a)):
            if a[i]=='{' and a[i+1]=='{':
                i+=2
                while(a[i]!='}'):
                    s=s+a[i]
                    i+=1
            if s!='' and s not in l:
                l.append(s)
            s=''
    # populate(filename)
    return render_template('inputypes.html',l=l)


# populating and downloading the file
@app.route('/populate', methods=['GET','POST'])
@login_required
def populate():
    filename = request.form.get('filename')
    
    
    context={}
    cont = request.form
    for i,j in cont.items():
        context[i]=j
    filename = request.form.get('filename')
    populate2(filename,context)
    return str(len(cont))
    

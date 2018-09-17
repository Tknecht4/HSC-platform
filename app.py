
# Echelon HSC Reporting Web Platform

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_user, LoginManager, UserMixin, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime
from config import Config
from forms import LoginForm, UploadForm
import pandas as pd
from flask_weasyprint import HTML, render_pdf
from flask.ext.uploads import configure_uploads, UploadSet, IMAGES, patch_request_class
import os

# build app
app = Flask(__name__, static_folder='/home/tknecht/mysite/static')
app.config.from_object(Config)
app.config['UPLOADED_IMAGES_DEST'] = '/home/tknecht/mysite/static/image/'
app.config['UPLOADED_CSVFILES_DEST'] = '/home/tknecht/mysite/static/csv/'
# import sqlalchemy features for new mysql, migration
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# initiate db and create app with login manager
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure the uploading with flask-uploads
# Flask-Uploads sets, default upload size to 32mb
images = UploadSet('images', IMAGES)
csv = UploadSet('csvfiles', 'csv')
configure_uploads(app, (images, csv))
patch_request_class(app, 32 * 1024 * 1024)


# define what a user looks like, create user table model, password checks
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.username

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username=user_id).first()

# define mysql models for db tables growers/fields. Can put this in another file later.
class Growers(db.Model):
    __tablename__ = 'growers'
    name = db.Column(db.String(250), nullable = False)
    division = db.Column(db.String(250))
    id = db.Column(db.Integer, primary_key = True)
    created = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    grower_fields = db.relationship('Fields', backref='fields', lazy='dynamic')

class Fields(db.Model):
    __tablename__ = 'fields'
    name = db.Column(db.String(250), nullable = False)
    id = db.Column(db.Integer, primary_key = True)
    crop = db.Column(db.String(100))
    crop_year = db.Column(db.Integer)
    map_img = db.Column(db.String(250))
    plot_img = db.Column(db.String(250))
    harvest_score = db.Column(db.Integer)
    variety = db.Column(db.String(100))
    is_vr = db.Column(db.Boolean())
    avg_yield = db.Column(db.Float(10))
    avg_n = db.Column(db.Float(10))
    harvest_acres = db.Column(db.Float(10))
    applied_acres = db.Column(db.Float(10))
    yield_data = db.Column(db.String(500))
    app_data = db.Column(db.String(500))
    grower_id = db.Column(db.Integer, db.ForeignKey('growers.id'))
    created = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_visible = db.Column(db.Boolean(), default = True)

# App functions
def ingestCSV(configcsv):
    df = pd.read_csv(configcsv, na_filter=False)

    # Check if valid file - test headers vs list then return if error
    # Most likely faster to query if grower exists outside of loop instead of running everytime for a config file.. as long as people don't mess with config?
    # load records to database row by row

    for key,value in df.iterrows():
        #map row values to dictionary format
        grower_name = value['Grower_Name']
        field_name = value['Field_Name']
        field_values = {'name': field_name, 'crop':value['Crop_Type'], 'avg_yield':value['Avg_Yield'], 'plot_img':value['Plot_Path'],
                'map_img':value['Img_Path'], 'yield_data':value['Yld_Vol_Data'], 'variety':value['Variety'], 'harvest_score':value['Harvest_Score'],
                'avg_N':float(value['Avg_N']), 'app_data':value['N_Apd_Data'], 'crop_year':value['Crop_Year'], 'is_vr':value['Is_VR'], 'user_id':current_user.id,
                'harvest_acres':float(value['Harvest_Acres']), 'applied_acres':float(value['Applied_Acres'])}
        grower_values = {'name': grower_name, 'division':value['Division'], 'user_id':current_user.id}

        #check if grower exists in db
        grower = Growers.query.filter_by(name=grower_name).first()
        if grower is not None:
            #check if field exists
            itemToEdit = Fields.query.filter_by(name=field_name).first()
            if itemToEdit is not None:
                #if the field exists we want to update existing record
                for key, value in field_values.items():
                    setattr(itemToEdit, key, value)
                itemToEdit.grower_id = grower.id
                db.session.add(itemToEdit)
                db.session.commit()
            else:
                #field does not exist but grower does
                newField = Fields()
                for key, value in field_values.items():
                    setattr(newField, key, value)
                newField.grower_id = grower.id
                db.session.add(newField)
                db.session.commit()
        else:
            #grower and field do not exist in db
            #make grower
            newGrower = Growers()
            for key, value in grower_values.items():
                setattr(newGrower, key, value)
            db.session.add(newGrower)
            db.session.commit()
            grower = Growers.query.filter_by(name=grower_name).first()
            newField = Fields()
            for key, value in field_values.items():
                setattr(newField, key, value)
            newField.grower_id = grower.id
            db.session.add(newField)
            db.session.commit()
    return grower

# start webapp, create login page and logout functionality
@app.route('/', methods=['GET','POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('division'))
    else:
        form = LoginForm()
        if request.method == 'GET':
            return render_template('login.html', error=False, form=form)
        user = load_user(request.form["username"])
        if user is None:
            return render_template('login.html', error=True, form=form)
        if not user.check_password(request.form["password"]):
            return render_template('login.html', error=True, form=form)
        login_user(user)
        return redirect(url_for('division'))

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# create index page listing available growers
@app.route('/<division>/index')
@login_required
def grower(division):
    items = Growers.query.filter_by(division = division).order_by("name").all()
    return render_template('index.html',division=division, items=items)

# create division list with link to index.html
@app.route('/division')
@login_required
def division():
    items = Growers.query.distinct(Growers.division).group_by(Growers.division).order_by("division")
    return render_template('division.html', items=items)

@app.route('/<division>/<int:grower_id>/')
@login_required
def growerRecord(division, grower_id):
    grower = Growers.query.filter_by(id = grower_id).one()
    items = Fields.query.filter_by(grower_id = grower_id).order_by("name")
    return render_template('grower.html',division=division, grower=grower, items=items)

# edit existing field
@app.route('/<division>/<int:grower_id>/<int:field_id>/edit/', methods=['GET','POST'])
@login_required
def editField(division, grower_id, field_id):
    editedItem = Fields.query.filter_by(id=field_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['crop']:
            editedItem.crop = request.form['crop']
        if request.form['variety']:
            editedItem.variety = request.form['variety']
        db.session.add(editedItem)
        db.session.commit()
        flash(editedItem.name + " successfully edited!")
        return redirect(url_for('growerRecord', division=division, grower_id=grower_id))
    else:
        return render_template('editfield.html', division=division, grower_id=grower_id, field_id=field_id, item=editedItem)

# hide a field
@app.route('/<division>/<int:grower_id>/<int:field_id>/hide/')
@login_required
def hideField(division, grower_id, field_id):
    itemToHide = Fields.query.filter_by(id=field_id).one()

    if itemToHide.is_visible == 1:
        itemToHide.is_visible = 0
    else:
        itemToHide.is_visible = 1
    db.session.add(itemToHide)
    db.session.commit()
    return redirect(url_for('growerRecord', division=division, grower_id=grower_id))

# Upload a csv file then ingest to db
@app.route('/upload', methods=['GET','POST'])
@login_required
def uploadFiles():

    form = UploadForm()
    if form.validate_on_submit():
        #process config file
        grower = ingestCSV(form.upl_csv.data)
        #save files to static
        for f in request.files.getlist('upl_imgs'):
            filepath = os.path.join(app.config['UPLOADED_IMAGES_DEST'], f.filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            images.save(f)
        flash("Files accepted and added to database.")
        return redirect(url_for('grower', division=grower.division, grower_id=grower.id))
    return render_template('upload.html', form=form)

# PDF generation
@app.route('/<division>/<int:grower_id>/pdf', methods=['GET', 'POST'])
@login_required
def gen_pdf(division, grower_id):
    toc = False
    if request.method == 'POST':
        if request.form.get('toc'):
            toc = True

        grower = db.session.query(Growers).filter(Growers.id == grower_id).one()
        pages = db.session.query(Fields).filter(Fields.grower_id == grower_id).order_by("name")
        html_out = render_template('report_template.html',pages = pages, grower=grower, toc=toc)
        return render_pdf(HTML(string=html_out), download_filename=(grower.name + ' 2018 Harvest Scorecard.pdf'))
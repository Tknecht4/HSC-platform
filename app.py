
# Echelon HSC Reporting Web Platform

from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_user, LoginManager, UserMixin, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime
from config import Config
from forms import LoginForm, UploadForm
import pandas as pd
from flask_weasyprint import HTML, render_pdf
from flask_uploads import configure_uploads, UploadSet, IMAGES, patch_request_class
import os
import csv as csvmod
import io

# Import sqlalchemy features for mysql connection and the database migration.
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, label
from sqlalchemy import distinct
from flask_migrate import Migrate

# Build app and set folder path configurations.
app = Flask(__name__, static_folder='/home/tknecht/mysite/static')
app.config.from_object(Config)
app.config['UPLOADED_IMAGES_DEST'] = '/home/tknecht/mysite/static/image/'
app.config['UPLOADED_CSVFILES_DEST'] = '/home/tknecht/mysite/static/csv/'
app.jinja_env.cache = {}

# Initiate db and create app with login manager.
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

# The following classes represent the database tables and how the SQLalchemy orm will interface.
# Define what a user looks like, create user table model, password checks.
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

# Define mysql models for db tables growers/fields. Can put this in another file later.
class Growers(db.Model):
    __tablename__ = 'growers'
    name = db.Column(db.String(250), nullable = False)
    division = db.Column(db.String(250))
    retail = db.Column(db.String(250))
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
    field_centroid = db.Column(db.String(100))
    map_img = db.Column(db.String(250))
    applied_map_img = db.Column(db.String(250))
    plot_img = db.Column(db.String(250))
    harvest_score = db.Column(db.Integer)
    variety = db.Column(db.String(100))
    is_vr = db.Column(db.Boolean())
    avg_yield = db.Column(db.Float(10))
    avg_n = db.Column(db.Float(10))
    harvest_acres = db.Column(db.Float(10))
    applied_acres = db.Column(db.Float(10))
    yield_data = db.Column(db.String(1200))
    app_data = db.Column(db.String(1200))
    grower_id = db.Column(db.Integer, db.ForeignKey('growers.id'))
    created = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_visible = db.Column(db.Boolean(), default = True)
    is_planting = db.Column(db.Boolean(), default = False)

# App functions
def ingestCSV(configcsv, divisionForm, retailForm, growerForm):
    df = pd.read_csv(configcsv, na_filter=False)

    # Check if valid file - test headers vs list then return if error.
    # Most likely faster to query if grower exists outside of loop instead of running everytime for a config file.. as long as people don't mess with config?
    # Load records to database row by row.
    crop_year = df.iloc[0]['Crop_Year']
    for key,value in df.iterrows():
        # Map row values to dictionary format.
        grower_name = growerForm
        field_name = value['Field_Name']
        field_values = {'name': field_name, 'crop':value['Crop_Type'], 'avg_yield':value['Avg_Yield'], 'plot_img':value['Plot_Path'].strip("'"),
                'map_img':value['Img_Path'].strip("'"), 'yield_data':value['Yld_Vol_Data'], 'variety':value['Variety'], 'harvest_score':value['Harvest_Score'],
                'avg_n':float(value['Avg_N']), 'app_data':value['N_Apd_Data'], 'crop_year':int(value['Crop_Year']), 'is_vr':value['Is_VR'], 'user_id':current_user.id,
                'harvest_acres':float(value['Harvest_Acres']), 'applied_acres':float(value['Applied_Acres']),'applied_map_img':value['Applied_Img_Path'].strip("'"),
                'field_centroid':value['Field_Centroid']}

        if len(field_values['crop']) == 0:
            field_values['crop'] = 'Unknown'
        if len(field_values['variety']) == 0:
            field_values['variety'] = 'Unknown'

        grower_values = {'name': grower_name, 'division':divisionForm, 'retail':retailForm, 'user_id':current_user.id}

        # Check if grower exists in db.
        grower = Growers.query.filter_by(name=grower_name).first()
        if grower is not None:
            # Check if field exists.
            itemToEdit = Fields.query.filter_by(name=field_name, crop_year=int(crop_year)).first()
            if itemToEdit is not None:
                # If the field exists we want to update existing record.
                for key, value in field_values.items():
                    setattr(itemToEdit, key, value)
                itemToEdit.grower_id = grower.id
                db.session.add(itemToEdit)
                db.session.commit()
            else:
                # Field does not exist but grower does.
                newField = Fields()
                for key, value in field_values.items():
                    setattr(newField, key, value)
                newField.grower_id = grower.id
                db.session.add(newField)
                db.session.commit()
        else:
            # Grower and field do not exist in db.
            # Make grower.
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
    return grower, crop_year

# Create global current year variable so when user clicks banner link it will reset to current year
current_year = datetime.now().year

# Start webapp, create login page and logout functionality.
@app.route('/', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('division', year=current_year))
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
        return redirect(url_for('division', year=current_year))

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Create division list with link to index.html.
@app.route('/<int:year>/division/')
@login_required
def division(year):
    # Gets list of available divisions for the selected year
    items = db.session.query(Growers).join(Fields).filter(Fields.crop_year==year).group_by(Growers.division).order_by("division")

    # Gets a list of years available to filter by
    archive_years = Fields.query.distinct(Fields.crop_year).group_by(Fields.crop_year)
    return render_template('division.html', items=items, year=year, current_year=current_year, archive_years=archive_years)

# Create index page listing available growers for that division.
@app.route('/<int:year>/<division>/index/')
@login_required
def grower(year, division):
    items = db.session.query(Growers).join(Fields).filter(Growers.division==division, Fields.crop_year==year).order_by(Growers.retail, Growers.name).all()
    return render_template('index.html', year=year, division=division, items=items, current_year=current_year)

# Create page listing all of the fields available for the grower in a table format.
@app.route('/<int:year>/<division>/<int:grower_id>/')
@login_required
def growerRecord(year, division, grower_id):
    grower = Growers.query.filter_by(id = grower_id).one()
    items = Fields.query.filter_by(grower_id = grower_id, crop_year = year).order_by("name")
    return render_template('grower.html', year=year, division=division, grower=grower, items=items, current_year=current_year)

# Edit existing field. Field name, crop type and variety.
@app.route('/<int:year>/<division>/<int:grower_id>/<int:field_id>/edit/', methods=['GET','POST'])
@login_required
def editField(year, division, grower_id, field_id):
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
        return redirect(url_for('growerRecord', division=division, grower_id=grower_id, year=year, current_year=current_year))
    else:
        return render_template('editfield.html', division=division, grower_id=grower_id, year=year,  field_id=field_id, item=editedItem, current_year=current_year)

# Hide a field to remove from the report.
@app.route('/<int:year>/<division>/<int:grower_id>/<int:field_id>/hide/')
@login_required
def hideField(year, division, grower_id, field_id):
    itemToHide = Fields.query.filter_by(id=field_id).one()

    if itemToHide.is_visible == 1:
        itemToHide.is_visible = 0
    else:
        itemToHide.is_visible = 1
    db.session.add(itemToHide)
    db.session.commit()
    return redirect(url_for('growerRecord', division=division, grower_id=grower_id, year=year, current_year=current_year))

#toggle flag for seed or fert.
@app.route('/<int:year>/<division>/<int:grower_id>/<int:field_id>/plantingfert/')
@login_required
def plantingfert(year, division, grower_id, field_id):
    itemToToggle = Fields.query.filter_by(id=field_id).one()

    if itemToToggle.is_planting == 1:
        itemToToggle.is_planting = 0
    else:
        itemToToggle.is_planting = 1
    db.session.add(itemToToggle)
    db.session.commit()
    return redirect(url_for('growerRecord', division=division, grower_id=grower_id, year=year, current_year=current_year))

# VR / Flat Rate Toggle Switch to add the tag on the report.
@app.route('/<int:year>/<division>/<int:grower_id>/<int:field_id>/toggleVR/')
@login_required
def toggleVR(year, division, grower_id, field_id):
    itemToToggle = Fields.query.filter_by(id=field_id).one()

    if itemToToggle.is_vr == 1:
        itemToToggle.is_vr = 0
    else:
        itemToToggle.is_vr = 1
    db.session.add(itemToToggle)
    db.session.commit()
    return redirect(url_for('growerRecord', division=division, grower_id=grower_id, year=year, current_year=current_year))

# Upload a csv file then ingest to db, take the image files and add to server local directory.
@app.route('/upload', methods=['GET','POST'])
@login_required
def uploadFiles():
    form = UploadForm()
    if form.validate_on_submit():
        #ingest form data
        grower_name = form.grower_name.data
        retail = form.retail_loc.data
        division = form.division_drop.data
        #process config file
        grower, crop_year = ingestCSV(form.upl_csv.data, division, retail, grower_name)
        #save files to static
        for f in request.files.getlist('upl_imgs'):
            filepath = os.path.join(app.config['UPLOADED_IMAGES_DEST'], f.filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            images.save(f)
        flash("Files accepted and added to database.")
        return redirect(url_for('growerRecord', division=grower.division, grower_id=grower.id, year=crop_year, current_year=current_year))
    return render_template('upload.html', form=form, current_year=current_year)

# PDF generation query. Checks if user wants table of contents then passes the query results into the report template.
@app.route('/<int:year>/<division>/<int:grower_id>/pdf/', methods=['GET', 'POST'])
@login_required
def gen_pdf(year, division, grower_id):
    toc = False
    if request.method == 'POST':
        if request.form.get('toc'):
            toc = True

        grower = db.session.query(Growers).filter(Growers.id == grower_id).one()
        pages = db.session.query(Fields).filter(Fields.grower_id == grower_id, Fields.crop_year == year).order_by("name")
        html_out = render_template('report_template.html',pages=pages, grower=grower, toc=toc, year=year)
        return render_pdf(HTML(string=html_out), download_filename=(grower.name + ' Harvest Scorecard.pdf'))

# Data dashboard page. Current numbers for each division.
@app.route('/dashboard')
@login_required
def dashboard():
    # division list
    divisions = Growers.query.distinct(Growers.division).group_by(Growers.division).order_by("division").all()
    crops = Fields.query.distinct(Fields.crop).group_by(Fields.crop).order_by("crop").all()

    # Get division summary stats
    def getDivisionStats(div_list):
        stats = []
        for div in div_list:
            stats.append(db.session.query(Growers.division, label('total_fields', func.count(Fields.id)),
                    label('total_growers', func.count(distinct(Growers.id))),
                    label('harvest_acres', func.sum(Fields.harvest_acres)),
                    label('applied_acres', func.sum(Fields.applied_acres))).join(Fields).filter(Growers.division==div.division).first())
        return stats

    # Get overall summary stats
    def getSummary():
        return db.session.query(label('total_fields', func.count(Fields.id)),
                    label('total_growers', func.count(distinct(Fields.grower_id))),
                    label('harvest_acres', func.sum(Fields.harvest_acres)),
                    label('applied_acres', func.sum(Fields.applied_acres))).first()

    return render_template('dashboard.html', summary=getSummary(), overallstats=getDivisionStats(divisions), crops=crops, current_year=current_year)

# Export a csv containing the relevant db information from the data dashboard page.
@app.route('/dashboard/export', methods=['GET', 'POST'])
@login_required
def export_csv():
    if request.method == 'POST':
        si = io.StringIO()
        outcsv = csvmod.writer(si)

        # Get joined table with all fields.
        result = db.session.query(Fields, Growers).join(Growers).order_by(Growers.name)

        # Column name list for the csv.
        outcsv.writerow(['Grower Name', 'Division', 'Retail', 'Field Name', 'Crop Type', 'Variety', 'Crop Year', 'Is VR', 'Harvest Score',
                            'Avg Yield', 'Avg N', 'Harvest Acres', 'Applied Acres', 'Yield Data', 'Applied Data', 'Creation Date', 'Is Planting', 'Is Visible'])
        for item in result:
            outcsv.writerow([item.Growers.name, item.Growers.division, item.Growers.retail, item.Fields.name, item.Fields.crop, item.Fields.variety, item.Fields.crop_year,
                                item.Fields.is_vr, item.Fields.harvest_score, item.Fields.avg_yield, item.Fields.avg_n, item.Fields.harvest_acres, item.Fields.applied_acres,
                                item.Fields.yield_data, item.Fields.app_data, item.Fields.created, item.Fields.is_planting, item.Fields.is_visible])
        response = make_response(si.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=Export.csv'
        response.headers["Content-type"] = "text/csv"
        return response

# Echelon HSC Reporting Web Platform

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_user, LoginManager, UserMixin, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime
from config import Config
from forms import LoginForm
import pandas as pd

# build app
app = Flask(__name__)
app.config.from_object(Config)

# import sqlalchemy features for new mysql, migration
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# initiate db and create app with login manager
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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
    variety = db.Column(db.String(50))
    is_vr = db.Column(db.Boolean())
    avg_yield = db.Column(db.Float)
    avg_n = db.Column(db.Float)
    yield_data = db.Column(db.String(500))
    app_data = db.Column(db.String(500))
    grower_id = db.Column(db.Integer, db.ForeignKey('growers.id'))
    created = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

# Build API Endpoint (GET Request)
'''@app.route('/<int:grower_id>/JSON')
def growerJSON(grower_id):
    items = session.query(Fields).filter_by(grower_id=grower_id).all()
    return jsonify(Field_List=[i.serialize for i in items])

@app.route('/<int:grower_id>/<int:field_id>/JSON')
def fieldJSON(grower_id, field_id):
    item = session.query(Fields).filter_by(id=field_id).one()
    return jsonify(Field_Record=item.serialize)'''

# start webapp, create login page and logout functionality
@app.route('/', methods=['GET','POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('grower'))
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
        return redirect(url_for('grower'))


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# create index page listing available growers
@app.route('/index')
@login_required
def grower():
    items = Growers.query.all()
    return render_template('index.html',items=items)

@app.route('/<int:grower_id>/')
@login_required
def growerRecord(grower_id):
    grower = Growers.query.filter_by(id = grower_id).one()
    items = Fields.query.filter_by(grower_id = grower_id)
    return render_template('grower.html',grower=grower, items=items)

# create a new field
@app.route('/<int:grower_id>/new/', methods=['GET','POST'])
@login_required
def newField(grower_id):
    if request.method == 'POST':
        newItem = Fields(name = request.form['name'], grower_id = grower_id, user_id=current_user.id)
        db.session.add(newItem)
        db.session.commit()
        flash("Successfully added " + newItem.name)
        return redirect(url_for('growerRecord', grower_id=grower_id))
    else:
        return render_template('newfield.html', grower_id=grower_id)

# edit existing field
@app.route('/<int:grower_id>/<int:field_id>/edit/', methods=['GET','POST'])
@login_required
def editField(grower_id, field_id):
    editedItem = Fields.query.filter_by(id=field_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['crop']:
            editedItem.crop = request.form['crop']
        db.session.add(editedItem)
        db.session.commit()
        flash(editedItem.name + " successfully edited!")
        return redirect(url_for('growerRecord', grower_id=grower_id))
    else:
        return render_template('editfield.html',grower_id=grower_id, field_id=field_id, item=editedItem)

# delete a field
@app.route('/<int:grower_id>/<int:field_id>/delete/', methods=['GET','POST'])
@login_required
def deleteField(grower_id, field_id):
    deletedItem = Fields.query.filter_by(id=field_id).one()
    if request.method == 'POST':
        db.session.delete(deletedItem)
        db.session.commit()
        flash(deletedItem.name + " deleted!")
        return redirect(url_for('growerRecord', grower_id=grower_id))
    else:
        return render_template('deletefield.html', grower_id=grower_id, field_id=field_id, item=deletedItem)

# Upload a csv file then ingest to db
@app.route('/upload', methods=['GET','POST'])
@login_required
def uploadCSV():
    if request.method =='POST':
        # Get the submitted csv
        df = pd.read_csv(request.files.get('file'))
        # Check if valid file - test headers vs list then return if error
        # Most likely faster to query if grower exists outside of loop instead of running everytime for a config file.. as long as people don't mess with config?
        # load records to database row by row

        for key,value in df.iterrows():
            #map row values to dictionary format
            field_values = {'name':value['Field_Name'], 'crop':value['Crop_Type'], 'avg_yield':value['Avg_Yield'], 'plot_img':value['Plot_Path'],
                    'map_img':value['Img_Path'], 'yield_data':value['Yld_Vol_Data'], 'variety':value['Variety'], 'harvest_score':value['Harvest_Score'],
                    'avg_N':value['Avg_N'], 'app_data':value['N_Apd_Data'], 'crop_year':value['Crop_Year'], 'is_vr':value['Is_VR'], 'user_id':current_user.id}
            grower_values = {'name':value['Grower_Name'], 'division':value['Division'], 'user_id':current_user.id}

            #check if grower exists in db
            grower = Growers.query.filter_by(name=value['Grower_Name']).first()
            if grower is not None:
                #check if field exists
                itemToEdit = Fields.query.filter_by(name=value['Field_Name']).first()
                if itemToEdit is not None:
                    #if the field exists we want to update existing record
                    for key, value in field_values.items():
                        setattr(itemToEdit, key, value)
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
                grower = Growers.query.filter_by(name=value['Grower_name']).first()
                newField = Fields()
                for key, value in field_values.items():
                    setattr(newField, key, value)
                newField.grower_id = grower.id
                db.session.add(newField)
                db.session.commit()

        flash("File accepted and added to database!")
        return redirect(url_for('growerRecord', grower_id=grower.id))
    else:
        return render_template('upload.html')

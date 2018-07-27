
# Echelon HSC Reporting Web Platform

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, LoginManager, UserMixin, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime
from config import Config
from forms import LoginForm

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
    map_blob = db.Column(db.LargeBinary)
    harvest_score = db.Column(db.Integer)
    variety = db.Column(db.String(50))
    is_vr = db.Column(db.Boolean())
    avg_yield = db.Column(db.Float)
    avg_n = db.Column(db.Float)
    report_path = db.Column(db.String(250))
    grower_id = db.Column(db.Integer, db.ForeignKey('growers.id'))
    created = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    field_data = db.relationship('Data', backref='data', lazy='dynamic')

class Data(db.Model):
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key = True)
    field_id = db.Column(db.Integer, db.ForeignKey('fields.id'))
    yield_data = db.Column(db.Float)
    app_data = db.Column(db.Float)
    order = db.Column(db.Integer)


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
        newItem = Fields(name = request.form['name'], grower_id = grower_id, user=current_user)
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


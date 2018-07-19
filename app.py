
#Echelon HSC Reporting Web Platform

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = '34tk56gj67'

#import sqlalchemy features for new mysql
from flask_sqlalchemy import SQLAlchemy

#build db connection
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="tknecht",
    password="echelon123",
    hostname="tknecht.mysql.pythonanywhere-services.com",
    databasename="tknecht$growers",)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

#define mysql models for db can put this in another file later
class Growers(db.Model):
    __tablename__ = 'growers'
    name = db.Column(db.String(250), nullable = False)
    id = db.Column(db.Integer, primary_key = True)

class Fields(db.Model):
    __tablename__ = 'fields'
    name = db.Column(db.String(250), nullable = False)
    id = db.Column(db.Integer, primary_key = True)
    crop = db.Column(db.String(250))
    grower_id = db.Column(db.Integer, db.ForeignKey('growers.id'))

#Build API Endpoint (GET Request)
'''@app.route('/<int:grower_id>/JSON')
def growerJSON(grower_id):
    items = session.query(Fields).filter_by(grower_id=grower_id).all()
    return jsonify(Field_List=[i.serialize for i in items])

@app.route('/<int:grower_id>/<int:field_id>/JSON')
def fieldJSON(grower_id, field_id):
    item = session.query(Fields).filter_by(id=field_id).one()
    return jsonify(Field_Record=item.serialize)'''

#start webapp
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', error=False)
    if request.form["username"] != "admin" or request.form["password"] != "admin":
        return render_template('login.html', error=True)
    return redirect(url_for('grower'))

@app.route('/index')
def grower():
    items = Growers.query.all()
    return render_template('index.html',items=items)

@app.route('/<int:grower_id>/')
def growerRecord(grower_id):
    grower = Growers.query.filter_by(id = grower_id).one()
    items = Fields.query.filter_by(grower_id = grower_id)
    return render_template('grower.html',grower=grower, items=items)

#create a new field
@app.route('/<int:grower_id>/new/', methods=['GET','POST'])
def newField(grower_id):
    if request.method == 'POST':
        newItem = Fields(name = request.form['name'], grower_id = grower_id)
        db.session.add(newItem)
        db.session.commit()
        flash("Successfully added " + newItem.name)
        return redirect(url_for('growerRecord', grower_id=grower_id))
    else:
        return render_template('newfield.html', grower_id=grower_id)

#edit existing field
@app.route('/<int:grower_id>/<int:field_id>/edit/', methods=['GET','POST'])
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

#delete a field
@app.route('/<int:grower_id>/<int:field_id>/delete/', methods=['GET','POST'])
def deleteField(grower_id, field_id):
    deletedItem = Fields.query.filter_by(id=field_id).one()
    if request.method == 'POST':
        db.session.delete(deletedItem)
        db.session.commit()
        flash(deletedItem.name + " deleted!")
        return redirect(url_for('growerRecord', grower_id=grower_id))
    else:
        return render_template('deletefield.html', grower_id=grower_id, field_id=field_id, item=deletedItem)


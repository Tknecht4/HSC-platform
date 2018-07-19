
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)

#import sqlalchemy features
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sql_database import Base, Growers, Fields
#build db connection
engine = create_engine('sqlite:////home/tknecht/mysite/growers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

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
@app.route('/')
def grower():
    items = session.query(Growers).all()
    return render_template('index.html',items=items)

@app.route('/<int:grower_id>/')
def growerRecord(grower_id):
    grower = session.query(Growers).filter_by(id = grower_id).one()
    items = session.query(Fields).filter_by(grower_id = grower_id)
    return render_template('grower.html',grower=grower, items=items)

#create a new field
@app.route('/<int:grower_id>/new/', methods=['GET','POST'])
def newField(grower_id):
    if request.method == 'POST':
        newItem = Fields(name = request.form['name'], grower_id = grower_id)
        session.add(newItem)
        session.commit()
        flash("Successfully added " + newItem.name)
        return redirect(url_for('growerRecord', grower_id=grower_id))
    else:
        return render_template('newfield.html', grower_id=grower_id)

#edit existing field
@app.route('/<int:grower_id>/<int:field_id>/edit/', methods=['GET','POST'])
def editField(grower_id, field_id):
    editedItem = session.query(Fields).filter_by(id=field_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['crop']:
            editedItem.crop = request.form['crop']
        session.add(editedItem)
        session.commit()
        flash(editedItem.name + " successfully edited!")
        return redirect(url_for('growerRecord', grower_id=grower_id))
    else:
        return render_template('editfield.html',grower_id=grower_id, field_id=field_id, item=editedItem)

#delete a field
@app.route('/<int:grower_id>/<int:field_id>/delete/', methods=['GET','POST'])
def deleteField(grower_id, field_id):
    deletedItem = session.query(Fields).filter_by(id=field_id).one()
    if request.method == 'POST':
        session.delete(deletedItem)
        session.commit()
        flash(deletedItem.name + " deleted!")
        return redirect(url_for('growerRecord', grower_id=grower_id))
    else:
        return render_template('deletefield.html', grower_id=grower_id, field_id=field_id, item=deletedItem)


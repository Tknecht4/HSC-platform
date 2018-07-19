import sys, os
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Growers(Base):
    __tablename__ = 'growers'
    name = Column(String(250), nullable = False)
    id = Column(Integer, primary_key = True)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
        }
class Fields(Base):
    __tablename__ = 'fields'
    name = Column(String(250), nullable = False)
    id = Column(Integer, primary_key = True)
    crop = Column(String(250))
    grower_id = Column(Integer, ForeignKey('growers.id'))
    grower = relationship(Growers)

    @property
    def serialize(self):
        #returns all objects into serializable format
        return {
            'name': self.name,
            'crop': self.crop,
            'id': self.id,
            'grower': self.grower_id,
        }
###insert at end of file ###
engine = create_engine('sqlite:////home/tknecht/mysite/growers.db')
Base.metadata.create_all(engine)


''' Manipulating the DB - need to run this code at start
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///home/tknecht/mysite/growers.db')
Base.metadata.bind=engine
DBSession = sessionmaker(bind = engine)
session = DBSession()
-----------------------
Common task examples CRUD
-----------------------
to Create a new record::
myFirstRestaurant = Restaurant(name = "Pizza Palace")
session.add(myFirstRestaurant)
sesssion.commit()
------------------------
to Read a record::
firstResult = session.query(Restaurant).first()
firstResult.name

items = session.query(MenuItem).all()
for item in items:
    print item.name
-------------------------
to Update a record::
veggieBurgers = session.query(MenuItem).filter_by(name= 'Veggie Burger')
for veggieBurger in veggieBurgers:
    print veggieBurger.id
    print veggieBurger.price
    print veggieBurger.restaurant.name
    print "\n"
UrbanVeggieBurger = session.query(MenuItem).filter_by(id=8).one()
UrbanVeggieBurger.price = '$2.99'
session.add(UrbanVeggieBurger)
session.commit()
-------------------------
to Delete a record::
spinach = session.query(MenuItem).filter_by(name = 'Spinach Ice Cream').one()
session.delete(spinach)
session.commit() '''

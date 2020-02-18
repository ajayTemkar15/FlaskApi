from sqlalchemy import Column, Integer, String, Table, create_engine, ForeignKey, func
from sqlalchemy.orm import sessionmaker, relationship, joinedload
from sqlalchemy.ext.declarative import declarative_base
from marshmallow import Schema, fields

from config import db_uri


#init DB
Base = declarative_base() #returns a base class (metaclass) & entites inherit from it
engine = create_engine(db_uri, echo=False) #connection to the DB
Base.metadata.bind = engine
Session = sessionmaker()
Session.configure(bind=engine) #session tracks all records you add or modify
session = Session()

#association tables
user_skills = Table('user_skills', Base.metadata, Column('user_id', ForeignKey('users.id')),
												  Column('skills_id', ForeignKey('skills.id')))

user_hobbies = Table('user_hobbies', Base.metadata, Column('user_id', ForeignKey('users.id')),
												  Column('hobbies_id', ForeignKey('hobbies.id')))

#MODELS 
class User(Base):
	__tablename__ = 'users'

	id = Column(Integer, primary_key=True)
	username = Column(String(20))
	email = Column(String(100))
	#many to many  users<->skills
	skills = relationship('Skill', secondary=user_skills, back_populates='users')
	hobbies = relationship('Hobbie', secondary=user_hobbies, back_populates='users')
	#one to one 
	profile_pic = relationship('Profile', uselist=False,\
								 back_populates="users", \
								 cascade="all, delete-orphan")
	#object-representation
	def __repr__(self):
		return "User(%r %r)" % (self.username, self.email)


class Skill(Base):
	__tablename__ = 'skills'

	id = Column(Integer, primary_key=True)
	skill_name = Column(String(30))
	users = relationship('User', secondary=user_skills, back_populates='skills')

	def __repr__(self):
		return "Skill(%r)" % (self.skill_name)


class Hobbie(Base):
	__tablename__ = 'hobbies'

	id = Column(Integer, primary_key=True)
	hobbie_name = Column(String(30))
	users = relationship('User', secondary=user_hobbies, back_populates='hobbies')

	def __repr__(self):
		return "Hobbie(%r)" % (self.hobbie_name)


class Profile(Base):
    __tablename__ = 'user_profile'

    id = Column(Integer, primary_key=True)
    u_id = Column('u_id', ForeignKey('users.id'))
    image = Column(String(50))
    users = relationship('User', uselist=False)

    def __repr__(self):
        return "Profile(%r %r)" % (self.image, self.u_id)

#Create Tables 
# Base.metadata.create_all(engine)

###SCHEMAS###  organization of data and realationship among them
class SkillSchema(Schema):
	id = fields.Int(load_only=True)
	skill_name = fields.String()


class HobbieSchema(Schema):
	id = fields.Int(load_only=True)
	hobbie_name = fields.String()


class ProfileSchema(Schema):
    id = fields.Int()
    u_id = fields.Int(load_only=True)
    image = fields.String()


class UserSchema(Schema):
	class Meta:
		ordered = True


	id = fields.Int()
	username = fields.String()
	email = fields.Email()
	skills = fields.List(fields.Nested("SkillSchema",))
	hobbies = fields.List(fields.Nested("HobbieSchema",))
	profile_pic = fields.Nested("ProfileSchema", only=('u_id', 'image'))



if __name__ == '__main__':
	# Base.metadata.drop_all(engine)
	Base.metadata.create_all(engine)

import os, uuid

from flask import Flask, request, jsonify, make_response
from config import UPLOAD_FOLDER
from models import session
from models import User, Skill, Hobbie, Profile,\
                   HobbieSchema, SkillSchema, ProfileSchema, UserSchema,\
                   user_skills, user_hobbies
from sqlalchemy.dialects import mysql
from sqlalchemy import exc
from flask_swagger_ui import get_swaggerui_blueprint
from werkzeug.utils import secure_filename


app = Flask(__name__)
#uploads
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --------------------------SWAGGER CONFIG----------------------------

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGER_BLUEPRINT = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "API"})
app.register_blueprint(SWAGGER_BLUEPRINT, url_prefix=SWAGGER_URL)

# ------------------------------END-----------------------------------



#schemas
user_schema = UserSchema()
user_schemas = UserSchema(many=True)
skill_schema = SkillSchema()
skill_schemas = SkillSchema(many=True)
image_schema = ProfileSchema()
image_schemas = ProfileSchema(many=True)


@app.route('/api/v1/users/all/', methods=['GET'])
def get_users():
    res = session.query(User).order_by(User.id).all()

    # stmt = session.query(User, func.group_concat(Skill.skill_name),\
    #                     func.group_concat(Hobbie.hobbie_name), Profile.image).\
    #                     join(user_skills, User.id==user_skills.c.user_id).\
    #                     join(Skill, Skill.id==user_skills.c.skills_id).\
    #                     join(user_hobbies, User.id==user_hobbies.c.user_id).\
    #                     join(Hobbie, Hobbie.id==user_hobbies.c.hobbies_id).\
    #                     join(Profile,Profile.u_id==User.id).\
    #                     group_by(User.id).all()

    # import pdb
    # pdb.set_trace()

    output = user_schemas.dump(res)

    return jsonify(output)

@app.route('/api/v1/user/<int:id>/', methods=['GET'])
def get_user(id):
    res = session.query(User).get(id)
    output = user_schema.dump(res)

    return jsonify(output)

@app.route('/api/v1/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    if (del_user := session.query(User).get(id)):
        session.delete(del_user)
        
        #delete user Image from uploads folder if exists
        try:
            filename = del_user.profile_pic.image
        except Exception as e:
            print(e)
            pass
        else:
            DELETE_IMAGE_PATH = '{}/{}'.format(UPLOAD_FOLDER, filename)
            os.remove(DELETE_IMAGE_PATH) 
        finally:
            session.commit()

        output = user_schema.dump(del_user)          
    else:
        output = {"ERROR":"USER DOES NOT EXISTS"}

    return jsonify(output)  

@app.route('/api/v1/user/add/', methods=['POST'])
def add_user():
    username = request.json['username']
    email = request.json['email']
    skills = request.json['skills']
    hobbies = request.json['hobbies']
    
    new_user = User(username=username, email=email)

    for skill in skills:
        skill_obj = session.query(Skill).get(skill['id'])
        new_user.skills.append(skill_obj)

    for hob in hobbies:
        hob_obj = session.query(Hobbie).get(hob['id'])
        new_user.hobbies.append(hob_obj)

    session.add(new_user)
    session.commit()
    op = user_schema.dump(new_user)

    return jsonify(op)

@app.route('/api/v1/user/<int:id>', methods=['PUT'])
def update_user(id):
    user_obj = session.query(User).get(id)
    username = request.json['username']
    email = request.json['email']
    skills = request.json['skills']
    hobbies = request.json['hobbies']
    #update
    user_obj.username = username
    user_obj.email = email
    user_obj.skills = []
    user_obj.hobbies = []
                              
    for skill in skills:
        skill_obj = session.query(Skill).get(skill['id'])
        user_obj.skills.append(skill_obj)

    for hob in hobbies:
        hob_obj = session.query(Hobbie).get(hob['id'])
        user_obj.hobbies.append(hob_obj)
    
    session.commit()
    output = user_schema.dump(user_obj)

    return jsonify(output)

@app.route('/api/v1/user/<int:id>/UploadImage/', methods=['POST','PUT'])
def upload_user_image(id):
    if request.method == 'POST' and request.files['file']:
        img = request.files['file']
        img_name = secure_filename(img.filename)

        #Renaming File and save
        discard, ext = os.path.splitext(img_name)
        basename = uuid.uuid4().hex
        new_name = ''.join('{}{}'.format(basename, ext))
        saved_path = os.path.join(app.config['UPLOAD_FOLDER'], new_name)
        img.save(saved_path)

        schema = ProfileSchema(only=('u_id', 'image'))

        # #save to db
        if session.query(User).filter(User.id == id).scalar() is not None:
            if (img_obj := session.query(Profile).filter(Profile.u_id == id).first()):
            # img_obj = session.query(Profile).filter(Profile.u_id == id).first()
                img_obj.image = new_name
                result = schema.dump(img_obj)
            else:
                user_img = Profile(u_id=id, image=new_name)
                session.add(user_img)
                result = schema.dump(user_img)
        else:
            result = {"ERROR": "USER DOES NOT EXISTS"}
  
        session.commit()        
        return jsonify(result)


if __name__ == '__main__':
    app.run()
    
#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
from flask_restful import Api, Resource
import os
from sqlalchemy import desc
from werkzeug.exceptions import HTTPException, NotFound, BadRequest


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

class Home(Resource):
    def get(self):
        return ('', 200)
    
class Campers(Resource):
    def get(self):
        camper_list = [{'id': camper.id,'name': camper.name,'age': camper.age, } for camper in Camper.query.all()]
        response = make_response(
            camper_list,
            200,
        )
        print(type(response))
        return response
    
    def post(self):
        try:
            data = request.get_json()
            new_camper = Camper(
                name = data["name"],
                age = data["age"]
            )
            if new_camper:
                db.session.add(new_camper)
                db.session.commit()
                camper_instance = Camper.query.filter_by(name = new_camper.to_dict()['name']).first()
                response = make_response(
                    camper_instance.to_dict(),
                    201,
                )
                return response
        except ValueError as e:
        # Handle model validation errors
            response = make_response({"errors": [str(e)]}, 400)
            return response

class IndividualCampers(Resource):
    def get(self, id):
        print(type(Camper))
        camper = Camper.query.filter_by(id=id).first()
        if camper is None:
            return make_response({"error": "Camper not found"}, 404)
        return (camper.to_dict(), 200)
        
    def patch(self, id):
        try:
            camper =  Camper.query.filter_by(id = id).first()
            if camper is None:
                return({'error': 'Camper not found'}, 404)
            data = request.get_json()

            if 'name' in data:
                camper.name = data['name']
            if 'age' in data:
                camper.age = data['age']

            camper_dict = camper.to_dict()
            camper_obj = {
                'name': camper_dict['name'],
                'id': camper_dict['id'],
                'age': camper_dict['age']
            }
            db.session.commit()
            response = make_response(
                camper_obj,
                202
            )
            return response
        except ValueError as e:
            response = make_response({"errors": ['validation errors']}, 400)
            return response


class Activities(Resource):
    def get(self):
        activity_list = ([{'id': activity.id, 'name': activity.name, 'difficulty': activity.difficulty} for activity in Activity.query.all()])
        response = make_response(activity_list, 200)
        return response
    
class IndividualActivity(Resource):
    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()
        if activity is None:
            return ({"error": "Activity not found"}, 404)
        # db.session.delete(activity.signups)
        db.session.delete(activity)
        print(activity.signups)
        db.session.commit()
        return ({}, 204)

class Signups(Resource):
    def get(self):
        return ([signup.to_dict() for signup in Signup.query.all()], 200)
    def post(self):
        try:
            data = request.get_json()
            print(data)
            new_signup = Signup(
                camper_id = data["camper_id"],
                activity_id = data["activity_id"],
                time = data["time"]
            )
            if new_signup:
                print("New Signup")
                db.session.add(new_signup)
                db.session.commit()
                new_signup_item = Signup.query.order_by(desc(Signup.id)).first()
            
                response_item = {
                        "id": new_signup_item.id,
                        "camper_id": new_signup_item.camper_id,
                        "activity_id": new_signup_item.activity_id,
                        "time": new_signup_item.time,
                        "activity" : new_signup_item.activity.to_dict(),
                        "camper": new_signup_item.camper.to_dict()
                }
                print(response_item)
                response  = make_response(response_item, 201)
                return response
        except ValueError as e:
            response = make_response({"errors": ['validation errors']}, 400)
            return response  
      
        
api.add_resource(Campers,'/campers')
api.add_resource(IndividualCampers, '/campers/<int:id>')
api.add_resource(Activities, '/activities')
api.add_resource(IndividualActivity, '/activities/<int:id>')
api.add_resource(Signups, '/signups')
if __name__ == '__main__':
    app.run(port=5555, debug=True)

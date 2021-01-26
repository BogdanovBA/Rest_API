from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp


app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'super-secret'


users = [
    {
        'id': 1,
        'username': 'Bob',
        'password': 'password123'
    },
    {
        'id': 2,
        'username': 'John',
        'password': 'password5555'
    },
    {
        'id': 3,
        'username': 'Alex',
        'password': 'password77777'
    }
]
cars = [
    {
        "id": 1,
        "mark": "BMW",
        "max_speed": 200,
        "distance": 500,
        "handler": "Auto Motors",
        "stock": "Germany"
    },
    {
        "id": 2,
        "mark": "Lada",
        "max_speed": 180,
        "distance": 350,
        "handler": "Avtovaz",
        "stock": "Russia"
    },
    {
        "id": 3,
        "mark": "Kia",
        "max_speed": 270,
        "distance": 550,
        "handler": "Hyundai",
        "stock": "Korea"
    }
]


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id



username_table = {u['username']: u for u in users}
userid_table = {u['id']: u for u in users}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


jwt = JWT(app, authenticate, identity)


class Automobile(Resource):
    @jwt_required()
    def get(self, mark):
        for car in cars:
            if car['mark'] == mark:
                return car, 200
        return {"Error": "Auto with that mark not found"}, 404

    @jwt_required()
    def post(self, mark):
        parser = reqparse.RequestParser()
        parser.add_argument('max_speed')
        parser.add_argument('distance')
        parser.add_argument('handler')
        parser.add_argument('stock')
        last_id = cars[-1]['id']
        new_car = parser.parse_args()
        for car in cars:
            if new_car['mark'] == car['mark']:
                return {"Error": "Auto with that mark exists"}, 400
            else:
                new_car['id'] = last_id+1
                new_car['mark'] = mark
                cars.append(new_car)
                return {"Message": "Auto created"}, 201

    @jwt_required()
    def put(self, mark):
        parser = reqparse.RequestParser()
        parser.add_argument('max_speed')
        parser.add_argument('distance')
        parser.add_argument('handler')
        parser.add_argument('stock')
        new_data = parser.parse_args()
        for car in cars:
            if car["mark"] == mark:
                car["max_speed"] = new_data["max_speed"] if new_data["max_speed"] else car["max_speed"]
                car["distance"] = new_data["distance"] if new_data["distance"] else car["distance"]
                car["handler"] = new_data["handler"] if new_data["handler"] else car["handler"]
                car["stock"] = new_data["stock"] if new_data["stock"] else car["stock"]
                return {"Message": "Auto updated"}, 202
        return {"Error": "Auto with that mark not found"}, 404

    @jwt_required()
    def delete(self, mark):
        for car in cars:
            if car['mark'] == mark:
                cars.remove(car)
                return {"Message": "Auto deleted"}, 202
        return {"Error": "Auto with that mark not found"}, 404


class AllCars(Resource):
    @jwt_required()
    def get(self):
        if len(cars) > 0:
            return cars, 200
        else:
            return {"Error": "No one autos found in DataBase"}, 400


class Users(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username')
        parser.add_argument('password')
        last_id = users[-1]['id']
        new_user = parser.parse_args()
        if new_user['username'] == users['username']:
            return {"Error": "User already exists"}, 400
        else:
            new_user['id'] = last_id+1
            users.append(new_user)
            return {"Message" : "User created. Try to auth"}, 201


api.add_resource(Automobile, '/auto/<string:mark>')
api.add_resource(Users, '/register')
api.add_resource(AllCars, '/stock')


if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token, jwt_required
from flask_cors import CORS


app = Flask(__name__)
api = Api(app)
app.config['JWT_SECRET_KEY'] = 'my_cool_secret'
jwt = JWTManager(app)
CORS(app)


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


class UserLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username')
        parser.add_argument('password')
        alien_user = parser.parse_args()
        for user in users:
            if user['username'] == alien_user['username'] and user['password'] == alien_user['password']:
                access_token = create_access_token(identity={
                    'role': 'admin',
                }, expires_delta=False)
                result = {'token': access_token}
                return result
            return {'error': 'Invalid username and password'}, 403


class Automobile(Resource):
    @jwt_required
    def get(self, mark):
        for car in cars:
            if car['mark'] == mark:
                return car, 200
        return {"Error": "Auto with that mark not found"}, 404

    @jwt_required
    def post(self, mark=''):
        parser = reqparse.RequestParser()
        parser.add_argument('mark')
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

    @jwt_required
    def put(self, mark=''):
        parser = reqparse.RequestParser()
        parser.add_argument('mark')
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

    @jwt_required
    def delete(self, mark=''):
        for car in cars:
            if car['mark'] == mark:
                cars.remove(car)
                return {"Message": "Auto deleted"}, 202
        return {"Error": "Auto with that mark not found"}, 404


class AllCars(Resource):
    @jwt_required
    def get(self):
        if len(cars) > 0:
            return cars, 200
        else:
            return {"Error": "No one autos found in DataBase"}, 400


class UsersRegister(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username')
        parser.add_argument('password')
        last_id = users[-1]['id']
        new_user = parser.parse_args()
        for user in users:
            if new_user['username'] == user['username']:
                return {"Error": "User already exists"}, 400
            else:
                new_user['id'] = last_id + 1
                users.append(new_user)
                return {"Message": "User created. Try to auth"}, 201


api.add_resource(Automobile, '/auto/<string:mark>')
api.add_resource(UsersRegister, '/register')
api.add_resource(AllCars, '/stock')
api.add_resource(UserLogin, '/auth')


if __name__ == '__main__':
    app.run(debug=True, port=8000)
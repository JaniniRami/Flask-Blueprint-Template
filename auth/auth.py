import jwt
import json
import datetime
from bson import json_util
from flask import Blueprint, jsonify, request, make_response
from flask_bcrypt import Bcrypt
from database import mongo



auth = Blueprint("auth", __name__)
bcrypt = Bcrypt()
users = mongo.db.users


def parse_bson(data):
    return json.loads(json_util.dumps(data))

@auth.route("/login", methods=["POST"])
def login():
    content_type = request.headers.get("Content-Type")

    if content_type == "application/json":
        try:
            credentials = request.get_json()
        except Exception as e:
            return jsonify({"message": "Invalid JSON"}), 400

        try:
            cleaned_credentials = {
                "email": credentials["email"],
                "password": credentials["password"],
            }
        except KeyError:
            return jsonify({"message": "Missing credentials"}), 400

        if cleaned_credentials["email"] and cleaned_credentials["password"]:
            user = users.find_one({"email": cleaned_credentials["email"]})
            user = parse_bson(user)
            if user:
                if bcrypt.check_password_hash(
                    user["password"], cleaned_credentials["password"]
                ):
                    jwt_token = jwt.encode(
                        {
                            "user_id" : user['_id']['$oid'],
                            "username": user["username"],
                            "watch_list": user["watch_list"],
                            "watched": user["watched"],
                            "exp": datetime.datetime.utcnow()
                            + datetime.timedelta(minutes=1),
                        },
                        "topsecret",
                    )
                    response = make_response(
                        jsonify({"message": "Successfully logged in."}), 200
                    )
                    response.set_cookie(
                        "access_token", jwt_token, httponly=True, samesite="Strict"
                    )
                    return response
                else:
                    return make_response(
                        jsonify({"message": "Incorrect password."}), 401
                    )
            else:
                return make_response(jsonify({"message": "User does not exist."}), 401)
    else:
        return jsonify({"message": "Content-Type must be application/json"}), 400


@auth.route("/register", methods=["POST"])
def register():
    content_type = request.headers.get("Content-Type")

    if content_type == "application/json":
        try:
            credentials = request.get_json()
        except Exception as e:
            return jsonify({"message": "Invalid JSON"}), 400
        try:
            cleaned_credentials = {
                "username": credentials["username"],
                "email": credentials["email"],
                "password": credentials["password"],
                "watch_list": credentials["watch_list"],
                "watched": credentials["watched"],
                "register_date": credentials["register_date"],
            }
        except KeyError:
            return make_response(jsonify({"message": "Missing credentials."}), 400)

        user = users.find_one({"email": cleaned_credentials["email"]})
        if user:
            return make_response(
                jsonify({"message": "User with this email already exists."}), 409
            )
        else:
            cleaned_credentials["password"] = bcrypt.generate_password_hash(
                cleaned_credentials["password"]
            ).decode("utf-8")
            users.insert_one(cleaned_credentials)
            return jsonify({"message": "User registered successfully"}), 201
    else:
        return jsonify({"message": "Content-Type must be application/json"}), 400

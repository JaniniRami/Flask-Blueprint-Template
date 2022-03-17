import jwt
from flask import Blueprint, request, jsonify, make_response
from functools import wraps
from database import mongo

api = Blueprint("api", __name__)
users = mongo.db.users

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        jwt_token = request.cookies.get("access_token")
        if not jwt_token:
            return jsonify({"message": "Missing token"}), 403
        else:
            try:
                data = jwt.decode(jwt_token, "topsecret", algorithms=["HS256"])
                return jsonify(data)
            except:
                return jsonify({"message": "Invalid token"}), 403

        return f(*args, **kwargs)

    return decorated

@api.route("/ping")
@token_required
def ping():
    return jsonify({"message": "This is a secret pong."})

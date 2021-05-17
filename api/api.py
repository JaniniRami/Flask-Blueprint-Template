from flask import Blueprint
from flask import jsonify

api = Blueprint('api', __name__)

@api.route('/api/ping')
def ping():
    return jsonify({'response' : 'pong!'})


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token') #http://adf.com/route!token=dsadfadsfa
        if not token:
            return jsonify({'resp': 'token is missing'}), 403
        try:
            data = jwt.decode(token, 'secretkey', algorithms=['HS256'])
        except:
            return jsonify({'resp': 'token is not valid'}), 403
        
        return f(*args, **kwargs)
    return decorated


@auth.route('/unprotected')

def unprotected():
    return jsonify({'resp': 'anyone can view this'})

@auth.route('/protected')
@token_required
def protected():
    return jsonify({'resp': 'this is only available for people with the token'})


@auth.route('/login')
def login():
    auth = request.authorization

    if auth and auth.password == 'secret':
        # logged in correctly
        token = jwt.encode({'user': auth.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, 'secretkey')

        return jsonify({'token': token})


    # not logged in
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

    return ''
#!/usr/bin/env python3
from app import app, db, jwt
from app.models import User, Item, Category
import httplib2
import hashlib
import hmac
from flask import request, jsonify
import os
import json
from flask_jwt_extended import (
    jwt_required, create_access_token, jwt_refresh_token_required,
    get_jwt_identity, create_refresh_token, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies)


# CHANGE THIS TO USE JOINS OR SOMETHING IN THE DB

@app.route('/')
@app.route('/home')
def home():
    categories = Category.query.all()
    categoriesArr = []
    for c in categories:
        items = c.items.all()
        categorySerial = c.serialize
        categorySerial['items'] = [x.serialize for x in items]
        categoriesArr.append(categorySerial)

    return jsonify(categories=categoriesArr), 200


@app.route('/items')
def items():
    items = Item.query.all()
    return jsonify(items=[i.serialize for i in items]), 200


# FB login
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    # verify Authorization Token
    verified_token = verifyFBToken(request)
    if verified_token[1] == 401:
        return verified_token[0], 401
    # Retrieve user information
    access_token = request.headers.environ['HTTP_AUTHORIZATION'].split('Bearer ')[1]  # noqa
    fb_user_id = verified_token[0]
    app_secret = os.environ.get('FB_APP_SECRET')
    app_secret_proof = generateAppSecretProof(app_secret, access_token)
    url = 'https://graph.facebook.com/%s?fields=name,email,picture&access_token=%s&appsecret_proof=%s' % (  # noqa
        fb_user_id, access_token, app_secret_proof)
    h = httplib2.Http()
    results = h.request(url, 'GET')[1]
    user_profile = json.loads(results)
    user_id = getUserID(user_profile['email'])
    if not user_id:
        user_id = createUser(user_profile)
    # create the tokens we will send back to the user
    jwt_access_token = create_access_token(identity=user_id)
    jwt_refresh_token = create_refresh_token(identity=user_id)

    # Set the jwt cookies in response
    response = jsonify(user_id)
    set_access_cookies(response, jwt_access_token, max_age=3600)
    set_refresh_cookies(response, jwt_refresh_token, max_age=3600)
    return response, 200


# FB delete user permission for the App
@app.route('/fbdelete', methods=['POST'])
def fbDeletePermission():
    facebook_id = request.json['data']['id']
    access_token = request.headers.environ['HTTP_AUTHORIZATION'].split('Bearer ')[1]  # noqa
    app_secret = os.environ.get('FB_APP_SECRET')
    app_secret_proof = generateAppSecretProof(app_secret, access_token)
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s&appsecret_proof=%s' % (  # noqa
        facebook_id, access_token, app_secret_proof)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    print(result)
    return 'User permissions Deleted', 200


# Read Items
@app.route('/categories/<int:category_id>/items')
def readItems(category_id):
    try:
        items = Item.query.filter_by(category_id=category_id).all()
        return jsonify(items=[i.serialize for i in items]), 200
    except:
        return 'Invalid ID', 401


# Create Item
@app.route('/categories/<int:category_id>/items', methods=['POST'])
@jwt_required
def addItem(category_id):
    try:
        user_id = get_jwt_identity()
        data = request.json
        newItem = Item(name=data['name'], description=data['description'],
                       picture=data['picture'], category_id=data['categoryId'],
                       user_id=user_id)
        db.session.add(newItem)
        db.session.commit()
        item = Item.query.filter_by(name=data['name']).first()
        return jsonify(item=item.serialize), 200
    except:
        return 'Invalid input for creating item', 401


# Read Item
@app.route('/categories/<int:category_id>/items/<int:item_id>')
def readItem(category_id, item_id):
    try:
        item = Item.query.filter_by(id=item_id).first()
        return jsonify(item=item.serialize), 200
    except:
        return 'Invalid ID', 401


# Update Item
@app.route('/categories/<int:category_id>/items/<int:item_id>', methods=['PUT'])  # noqa
@jwt_required
def updateItem(category_id, item_id):
    try:
        user_id = get_jwt_identity()
        data = request.json
        item = Item.query.filter_by(id=item_id).first()
        if item.user_id != user_id:
            return 'Invalid user; not owner of resource', 401
        if 'name' in data:
            item.name = data['name']
        if 'description' in data:
            item.description = data['description']
        if 'picture' in data:
            item.picture = data['picture']
        if 'categoryId' in data:
            item.category_id = data['categoryId']
        db.session.add(item)
        db.session.commit()
        return jsonify(item.serialize), 200
    except:
        return 'Invalid ID', 401


# Delete Item
@app.route('/categories/<int:category_id>/items/<int:item_id>', methods=['DELETE'])  # noqa
@jwt_required
def deleteItem(category_id, item_id):
    try:
        # USERID FROM JWT
        user_id = get_jwt_identity()
        item = Item.query.filter_by(id=item_id).first()
        if item.user_id != user_id:
            return 'invalid user; not owner of resource', 401
        db.session.delete(item)
        db.session.commit()
        return 'Item succesfully deleted', 200
    except:
        return 'Invalid ID', 401


# Create Category
@app.route('/categories', methods=['POST'])
@jwt_required
def addCategory():
    try:
        user_id = get_jwt_identity()
        data = request.json
        user = User.query.filter_by(id=user_id).first()
        if user.role != 'admin':
            return 'Invalid Role for this operation', 401
        newCategory = Category(name=data['name'], description=data['description'],  # noqa
                               picture=data['picture'])
        db.session.add(newCategory)
        db.session.commit()
        category = Category.query.filter_by(name=data['name']).first()
        return jsonify(category=category.serialize), 200
    except:
        return 'Invalid Input for creating category', 401


# Read Categories
@app.route('/categories', methods=['GET'])
def readCategories():
    categories = Category.query.all()
    return jsonify(categories=[c.serialize for c in categories])


# Read Category
@app.route('/categories/<int:category_id>', methods=['GET'])
def readCategory(category_id):
    try:
        category = Category.query.filter_by(id=category_id).first()
        return jsonify(category.serialize), 200
    except:
        return 'Invalid ID', 401


# Update Category
@app.route('/categories/<int:category_id>', methods=['PUT'])
@jwt_required
def updateCategory(category_id):
    try:
        user_id = get_jwt_identity()
        data = request.json
        user = User.query.filter_by(id=user_id).first()
        category = Category.query.filter_by(id=category_id).first()
        if user.role != 'admin':
            return 'Invalid role for this operation', 401
        if 'name' in data:
            category.name = data['name']
        if 'description' in data:
            category.description = data['description']
        if 'picture' in data:
            category.picture = data['picture']
        db.session.add(category)
        db.session.commit()
        return jsonify(category.serialize), 200
    except:
        return 'Invalid ID', 401


# Delete Category
@app.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required
def deleteCategory(category_id):
    try:
        user_id = get_jwt_identity()
        data = request.json
        user = User.query.filter_by(id=user_id).one()
        category = Category.query.filter_by(id=category_id).one()
        if user.role != 'admin':
            return 'Invalid role for this operation', 401
        db.session.delete(category)
        db.session.commit()
        return 'Category successfully delete', 200
    except:
        return 'Invalid ID', 401


# Same thing as login here, except we are only setting a new cookie
# for the access token.
@app.route('/token/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    # Create the new access token
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    # Set the JWT access cookie in the response
    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)
    return resp, 200


# Because the JWTs are stored in an httponly cookie now, we cannot
# log the user out by simply deleting the cookie in the frontend.
# We need the backend to send us a response to delete the cookies
# in order to logout. unset_jwt_cookies is a helper function to
# do just that.
@app.route('/token/remove', methods=['POST'])
def logout():
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200


# Verifies the fb access token send by client
def verifyFBToken(request):
    try:
        # Check if the Authorization header is on the request
        access_token = request.headers.environ['HTTP_AUTHORIZATION'].split('Bearer ')[1]  # noqa
        if access_token == 'undefined':
            return 'Missing Access Token from header', 401
        # Verify Request token
        app_id = os.environ.get('FB_APP_ID')
        app_secret = os.environ.get('FB_APP_SECRET')
        url = 'https://graph.facebook.com/debug_token?input_token=%s&access_token=%s|%s' % (  # noqa
            access_token, app_id, app_secret)
        h = httplib2.Http()
        results = h.request(url, 'GET')[1]
        verified_token = json.loads(results)['data']
        # Checks if the app_id on the token is the same as our app_id
        if (verified_token['app_id'] != app_id):
            return 'App id does not match real app id', 401
        # Check if the token send by client is still valid
        if (verified_token['is_valid'] is not True):
            return 'Verified token is invalid', 401
        # Token is valid
        return verified_token['user_id'], 200
    except KeyError:
        return 'Another Error', 401


def getUserID(email):
    try:
        user = User.query.filter_by(email=email).first()
        return user.id
    except:
        return None


def createUser(user):
    newUser = User(email=user['email'], name=user['name'],
                   picture=user['picture']['data']['url'])
    db.session.add(newUser)
    db.session.commit()
    user = User.query.filter_by(email=user['email']).first()
    return user.id


def getUserInfo(user_id):
    user = user.query.filter_by(id=user_id).first()
    return user


# FB developer guide recommends server to server request to use this
def generateAppSecretProof(app_secret, access_token):
    h = hmac.new(
        app_secret.encode('utf-8'),
        msg=access_token.encode('utf-8'),
        digestmod=hashlib.sha256
    )
    return h.hexdigest()

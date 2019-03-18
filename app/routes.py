#!/usr/bin/env python3
from app import app, db
from app.models import User, Item, Category
import httplib2
import hashlib
import hmac
from flask import request, jsonify
import os
import json


@app.route('/')
@app.route('/home')
def home():
    categories = Category.query.all()
    items = Item.query.all()
    response = jsonify(categories=[r.serialize for r in categories], items=[
                       i.serialize for i in items])
    return response


@app.route('/items')
def items():
    items = Item.query.all()
    return jsonify(items=[i.serialize for i in items])


# FB login
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    # verify Authorization Token
    verified_token = verifyToken(request)
    if verified_token is None:
        return 'Invalid Token'
    # Retrieve user information
    access_token = request.headers.environ['HTTP_AUTHORIZATION'].split('Bearer ')[1]  # noqa
    fb_user_id = verified_token['user_id']
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
    return jsonify(user_id)


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
    return 'User permissions Deleted'


# Create Item
@app.route('/categories/<int:category_id>/items', methods=['POST'])
def addItem(category_id):
    try:
        verified_token = verifyToken(request)
        if verified_token is None:
            return 'Invalid Token'
        data = request.json['data']
        newItem = Item(name=data['name'], description=data['description'],
                       picture=data['picture'], category_id=data['categoryId'],
                       user_id=data['userId'])
        db.session.add(newItem)
        db.session.commit()
        item = Item.query.filter_by(name=data['name']).first()
        return jsonify(item=item.serialize)
    except:
        return 'Invalid input for creating item'


# Read Items
@app.route('/categories/<int:category_id>/items')
def readItems(category_id):
    try:
        items = Item.query.filter_by(category_id=category_id).all()
        return jsonify(items=[i.serialize for i in items])
    except:
        return 'Invalid ID'


# Read Item
@app.route('/categories/<int:category_id>/items/<int:item_id>')
def readItem(category_id, item_id):
    try:
        item = Item.query.filter_by(id=item_id).first()
        return jsonify(item=item.serialize)
    except:
        return 'Invalid ID'


# Update Item
@app.route('/categories/<int:category_id>/items/<int:item_id>', methods=['PUT'])  # noqa
def updateItem(category_id, item_id):
    try:
        verified_token = verifyToken(request)
        if verified_token is None:
            return 'Invalid token'
        data = request.json['data']
        item = Item.query.filter_by(id=item_id).first()
        if item.user_id != data['userId']:
            return 'Invalid user; not owner of resource'
        if 'name' in data:
            item.name = data['name']
        if 'description' in data:
            item.description = data['description']
        if 'picture' in data:
            item.picture = data['picture']
        db.session.add(item)
        db.session.commit()
        return jsonify(item.serialize)
    except:
        return 'Invalid ID'


# Delete Item
@app.route('/categories/<int:category_id>/items/<int:item_id>', methods=['DELETE'])  # noqa
def deleteItem(category_id, item_id):
    try:
        verified_token = verifyToken(request)
        if verified_token is None:
            return 'invalid token'
        data = request.json['data']
        item = Item.query.filter_by(id=item_id).first()
        if item.user_id != data['userId']:
            return 'invalid user; not owner of resource'
        db.session.delete(item)
        db.session.commit()
        return 'Item succesfully deleted'
    except:
        return 'Invalid ID'


# Create Category
@app.route('/categories', methods=['POST'])
def addCategory():
    try:
        verified_token = verifyToken(request)
        if verified_token is None:
            return 'Invalid Token'
        data = request.json['data']
        user = User.query.filter_by(id=data['userId']).first()
        if user.role != 'admin':
            return 'Invalid Role for this operation'
        newCategory = Category(name=data['name'], description=data['description'],  # noqa
                               picture=data['picture'])
        db.session.add(newCategory)
        db.session.commit()
        category = Category.query.filter_by(name=data['name']).first()
        return jsonify(category=category.serialize)
    except:
        return 'Invalid Input for creating category'


# Read Category
@app.route('/categories/<int:category_id>', methods=['GET'])
def readCategory(category_id):
    try:
        category = Category.query.filter_by(id=category_id).first()
        return jsonify(category.serialize)
    except:
        return 'Invalid ID'


# Update Category
@app.route('/categories/<int:category_id>', methods=['PUT'])
def updateCategory(category_id):
    try:
        verified_token = verifyToken(request)
        if verified_token is None:
            return 'Invalid token'
        data = request.json['data']
        user = User.query.filter_by(id=data['userId']).first()
        category = Category.query.filter_by(id=category_id).first()
        if user.role != 'admin':
            return 'Invalid role for this operation'
        if 'name' in data:
            category.name = data['name']
        if 'description' in data:
            category.description = data['description']
        if 'picture' in data:
            category.picture = data['picture']
        db.session.add(category)
        db.session.commit()
        return jsonify(category.serialize)
    except:
        return 'Invalid ID'


# Delete Category
@app.route('/categories/<int:category_id>', methods=['DELETE'])
def deleteCategory(category_id):
    try:
        verified_token = verifyToken(request)
        if verified_token is None:
            return 'Invalid token'
        data = request.json['data']
        user = User.query.filter_by(id=data['userId']).one()
        category = Category.query.filter_by(id=category_id).one()
        if user.role != 'admin':
            return 'Invalid role for this operation'
        db.session.delete(category)
        db.session.commit()
        return 'Category successfully delete'
    except:
        return 'Invalid ID'


def verifyToken(request):
    try:
        # Check if the Authorization header is on the request
        access_token = request.headers.environ['HTTP_AUTHORIZATION'].split('Bearer ')[1]  # noqa
        if access_token == 'undefined':
            return None
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
            return None
        # Check if the token send by client is still valid
        if (verified_token['is_valid'] is not True):
            return None
        # Token is valid
        return verified_token
    except KeyError:
        return None


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

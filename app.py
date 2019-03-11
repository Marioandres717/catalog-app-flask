#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from db_setup import Base, User, Category, Item
from flask import session as login_session

import random
import string
import json
import httplib2
import requests
from datetime import datetime
from flask_cors import CORS
import hashlib
import hmac

app = Flask(__name__)
CORS(app)
engine = create_engine('sqlite:///store.db')
Base.metadata.bin = engine
DBSession = sessionmaker(bind=engine)


@app.route('/')
@app.route('/main')
def home():
    session = DBSession()
    categories = session.query(Category).all()
    items = session.query(Item).all()
    response = jsonify(categories=[r.serialize for r in categories], items=[
                       i.serialize for i in items])
    return response


@app.route('/users', methods=['GET'])
def user():
    session = DBSession()
    users = session.query(User).all()
    return jsonify(users=[u.serialize for u in users])


@app.route('/items')
def items():
    session = DBSession()
    items = session.query(Item).all()
    return jsonify(items=[i.serialize for i in items])


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    # verify Authorization Token
    verified_token = verifyToken(request)
    if verified_token is None:
        return 'Invalid Token'
    # Retrieve user information
    access_token = request.headers.environ['HTTP_AUTHORIZATION'].split('Bearer ')[1]  # noqa
    fb_user_id = verified_token['user_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_secret']
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


@app.route('/fbdelete', methods=['POST'])
def fbDeletePermission():
    facebook_id = request.json['data']['id']
    access_token = request.json['data']['accessToken']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    print(result)
    return 'User permissions Deleted'


# Create Item
@app.route('/item', methods=['POST'])
def addItem():
    verified_token = verifyToken(request)
    if verified_token is None:
        return 'Invalid Token'
    data = request.json['data']
    session = DBSession()
    newItem = Item(name=data['name'], description=data['description'],
                   picture=data['picture'], category_id=data['categoryId'],
                   user_id=data['userId'])
    session.add(newItem)
    session.commit()
    item = session.query(Item).filter_by(name=data['name']).one()
    return jsonify(item=item.serialize)


# Read Item
@app.route('/item/<int:item_id>', methods=['GET'])
def readItem(item_id):
    try:
        session = DBSession()
        item = session.query(Item).filter_by(id=item_id).one()
        return jsonify(item.serialize)
    except:
        return 'Invalid ID'


# Update Item
@app.route('/item/<int:item_id>', methods=['PUT'])
def updateItem(item_id):
    try:
        verified_token = verifyToken(request)
        if verified_token is None:
            return 'Invalid token'
        data = request.json['data']
        session = DBSession()
        item = session.query(Item).filter_by(id=item_id).one()
        if item.user_id != data['userId']:
            return 'Invalid user; not owner of resource'
        if 'name' in data:
            item.name = data['name']
        if 'name' in data:
            item.description = data['description']
        if 'picture' in data:
            item.picture = data['picture']
        session.add(item)
        session.commit()
        return jsonify(item.serialize)
    except:
        return 'Invalid ID'


# Delete Item
@app.route('/item/<int:item_id>', methods=['DELETE'])
def deleteItem(item_id):
    try:
        verified_token = verifyToken(request)
        if verified_token is None:
            return 'invalid token'
        data = request.json['data']
        session = DBSession()
        item = session.query(Item).filter_by(id=item_id).one()
        if item.user_id != data['userId']:
            return 'invalid user; not owner of resource'
        session.delete(item)
        session.commit()
        return 'Item succesfully deleted'
    except:
        return 'Invalid ID'


# Create Category
@app.route('/category', methods=['POST'])
def addCategory():
    verified_token = verifyToken(request)
    if verified_token is None:
        return 'Invalid Token'
    data = request.json['data']
    session = DBSession()
    user = session.query(User).filter_by(id=data['userId'])
    if user.role != 'admin':
        return 'Invalid Role for this operation'
    newCategory = Category(name=data['name'], description=data['description'],
                           picture=data['picture'])
    session.add(newCategory)
    session.commit()
    category = session.query(Category).filter_by(name=data['name']).one()
    return jsonify(category=category.serialize)


def verifyToken(request):
    try:
        # Check if the Authorization header is on the request
        access_token = request.headers.environ['HTTP_AUTHORIZATION'].split('Bearer ')[1]  # noqa
        if access_token == 'undefined':
            return None
        # Verify Request token
        app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
            'web']['app_id']
        app_secret = json.loads(open('fb_client_secrets.json', 'r').read())[
            'web']['app_secret']
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
        session = DBSession()
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def createUser(user):
    session = DBSession()
    newUser = User(email=user['email'], name=user['name'],
                   picture=user['picture']['data']['url'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=user['email']).one()
    return user.id


def getUserInfo(user_id):
    session = DBSession()
    user = session.query(user).filter_by(id=user_id).one()
    return user


def generateAppSecretProof(app_secret, access_token):
    h = hmac.new(
        app_secret.encode('utf-8'),
        msg=access_token.encode('utf-8'),
        digestmod=hashlib.sha256
    )
    return h.hexdigest()


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

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
    try:
        # Verify Request token
        access_token = request.json['data']
        app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
            'web']['app_id']
        app_secret = json.loads(open('fb_client_secrets.json', 'r').read())[
            'web']['app_secret']
        url = 'https://graph.facebook.com/debug_token?input_token=%s&access_token=%s|%s' % (  # noqa
            access_token, app_id, app_secret)
        h = httplib2.Http()
        results = h.request(url, 'GET')[1]
        verified_Token = json.loads(results)['data']
        # Checks if the app_id on the token is the same as our app_id
        if (verified_Token['app_id'] != app_id):
            return 'Invalid token'
        # Check if the token send by client is still valid
        if (verified_Token['is_valid'] is not True):
            return 'Invalid token'
        # Retrieve user information
        fb_user_id = verified_Token['user_id']
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
    except:
        return 'No access token found'


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

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
import re
from flask_cors import CORS

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
    return jsonify(categories=[r.serialize for r in categories])


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


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

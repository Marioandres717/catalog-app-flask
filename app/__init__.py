#!/usr/bin/env python3
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app, supports_credentials=True)
jwt = JWTManager(app)


from app import routes, models  # noqa

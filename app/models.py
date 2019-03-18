from app import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(80), index=True, unique=True, nullable=False)
    picture = db.Column(db.String(250))
    role = db.Column(db.String(80), default="normal", nullable=False)
    items = db.relationship('Item', backref='seller', lazy='dynamic')

    @property
    def serialize(self):
        """Return Object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture
        }

    def __repr__(self):
        return '<User {}>'.format(self.email)


class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), index=True, unique=True, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    picture = db.Column(db.String(250), nullable=False)
    items = db.relationship('Item', backref='category', lazy='dynamic')

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'picture': self.picture,
            'description': self.description
        }

    def __repr__(self):
        return '<Category {}>'.format(self.name)


class Item(db.Model):
    __tablename__ = 'item'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    picture = db.Column(db.String(250), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey(
        'category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'picture': self.picture,
            'description': self.description,
            'userId': self.user_id
        }

    def __repr__(self):
        return '<Item {}>'.format(self.name)

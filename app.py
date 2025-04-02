from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

API_KEY = os.getenv('API_KEY', 'mysecretapikey')

# Model
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

# Authentication middleware
def authenticate():
    api_key = request.headers.get('X-API-KEY')
    if not api_key or api_key != API_KEY:
        return jsonify({'Restricted': 'Access Unauthorized'}), 401

# Routes
@app.route('/', methods=['GET'])
def index():
    return jsonify(
        {
            'message': 'Welcome to our API', 
            'documentation': 'https://documenter.getpostman.com/view/24762258/2sB2cSfNjY',
            'access': 'use postman or curl',
        }
    )

@app.route('/items', methods=['GET'])
def get_items():

    items = Item.query.all()
    if items:
        return jsonify([{'id': item.id, 'name': item.name, 'description': item.description, 'price': item.price} for item in items]), 200
    return jsonify({'message': 'Database is empty'}), 200

@app.route('/retrieve/<int:item_id>', methods=['GET'])
def get_item(item_id):

    # item = Item.query.get(item_id)
    item = db.session.get(Item, item_id)
    if item:
        return jsonify({'id': item.id, 'name': item.name, 'description': item.description, 'price': item.price})
    return jsonify({'response': f'No data found for id: {item_id}'}), 404

@app.route('/create', methods=['POST'])
def create_item():
    auth = authenticate()
    if auth:
        return auth

    if not request.is_json:
        data = request.args.to_dict()
    else:
        data = request.json
        
    try:
        new_item = Item(name=data['name'], description=data['description'], price=float(data['price']))
        db.session.add(new_item)
        db.session.commit()
    except (KeyError, ValueError) as e:
        print(e)
        return jsonify({'message': f'{e.__doc__}: {e}'}), 400

    return jsonify({'message': 'Item created', 'id': new_item.id}), 201

@app.route('/replace/<int:item_id>', methods=['PUT'])
def replace_item(item_id):
    auth = authenticate()
    if auth:
        return auth

    item = Item.query.get(item_id)
    if not item:
        return jsonify({'message': 'item does not exist on server'}), 404
    if not request.is_json:
        data = request.args.to_dict()
    else:
        data = request.json
    
    try:
        item.name = data['name']
        item.description = data['description']
        item.price = float(data['price'])
        db.session.commit()
    except (KeyError, ValueError) as e:
        return jsonify({'message': f'{e.__doc__}: {e}'}), 400  
    
    return jsonify({'message': 'Item replaced'}), 200

@app.route('/amend/<int:item_id>', methods=['PATCH'])
def update_item(item_id):
    auth = authenticate()
    if auth:
        return auth

    item = Item.query.get(item_id)
    if not item:
        return jsonify({'message': 'item does not exist on server'}), 404
    if not request.is_json:
        data = request.args.to_dict()
    else:
        data = request.json
    item.name = data.get('name', item.name)
    item.description = data.get('description', item.description)
    item.price = data.get('price', item.price)
    db.session.commit()
    return jsonify({'message': 'Item updated'}), 200

@app.route('/delete/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    auth = authenticate()
    if auth:
        return auth

    item = Item.query.get(item_id)
    if not item:
        return jsonify({'message': 'item does not exist on server'}), 404
    
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': f'{item.name} deleted'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0')

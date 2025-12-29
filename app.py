import sys
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, ValidationError

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class DrinkSchema(Schema):
    name = fields.String(required=True)
    description = fields.String(required=True)

drink_schema = DrinkSchema()

# MODEL
class Drink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(120))

    # CRUD helpers (always safe)
    def save(self):
        with app.app_context():
            db.session.add(self)
            db.session.commit()

    def update(self, name=None, description=None):
        with app.app_context():
            if name:
                self.name = name
            if description:
                self.description = description
            db.session.commit()

    def delete(self):
        with app.app_context():
            db.session.delete(self)
            db.session.commit()

    def __repr__(self):
        return f"{self.id} | {self.name} - {self.description}"

#API Methods
@app.route('/')
def index():
    return  'Hello1'

@app.route('/drinks', methods=['POST'])
def add_drink():
    try:
        data = drink_schema.load(request.json)
    except ValidationError as err:
        return err.messages, 400

    drink = Drink(**data)
    drink.save()
    return drink_schema.dump(drink), 201


@app.route('/drinks/<id>')
def get_drink(id):
    drink = Drink.query.get_or_404(id)
    return {"name": drink.name, "description": drink.description},200

@app.route('/drinks', methods=['POST'])
def add_drink():
    drink = Drink(name = request.json['name'], description = request.json['description'])
    db.session.add(drink)
    db.session.commit()
    return {'id':drink.id},200


@app.route('/drinks/<int:id>', methods=['PUT'])
def update_drink(id):
    drink = Drink.query.get(id)

    if not drink:
        return {'error': 'Drink not found'}, 404

    data = request.get_json()

    drink.name = data.get('name', drink.name)
    drink.description = data.get('description', drink.description)

    db.session.commit()

    return {
        'id': drink.id,
        'name': drink.name,
        'description': drink.description
    },200

@app.route('/drinks/<int:id>', methods = ['PATCH'])
def patch_drinks(id):
    drink = Drink.query.get(id)

    if not drink:
        return {'Error':'Not found'},404
    data = request.get_json()

    if 'name' in data:
        drink.name = data['name']

    if 'description' in data:
        drink.description = data['description']

    db.session.commit()

    return {
        'id': drink.id,
        'name': drink.name,
        'description': drink.description
    },200

@app.route('/drinks/<id>', methods=['DELETE'])
def delete_drink(id):
    drink = Drink.query.get(id)
    if drink is None:
        return {"NO DRINK!!!"}
    db.session.delete(drink)
    db.session.commit()
    return {'Message': "DOne!!"},200

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}),404
@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Bad request"}), 400


# TERMINAL COMMAND FUNCTIONS
def create_db():
    with app.app_context():
        db.create_all()
    print("Database created!")


def add_drink(name, description):
    d = Drink(name=name, description=description)
    d.save()
    print("Drink added!")


def list_drinks():
    with app.app_context():
        drinks = Drink.query.all()
        for d in drinks:
            print(d)


def update_drink(drink_id, name, description):
    with app.app_context():
        drink = Drink.query.get(drink_id)
        if not drink:
            print("Drink not found!")
            return
        drink.update(name=name, description=description)
        print("Drink updated!")


def delete_drink(drink_id):
    with app.app_context():
        drink = Drink.query.get(drink_id)
        if not drink:
            print("Drink not found!")
            return
        drink.delete()
        print("Drink deleted!")


# PARSE TERMINAL COMMANDS
if __name__ == '__main__':
    args = sys.argv

    if len(args) < 2:
        print("Usage:")
        print("  python app.py create_db")
        print("  python app.py add \"Name\" \"Description\"")
        print("  python app.py list")
        print("  python app.py update <id> \"Name\" \"Description\"")
        print("  python app.py delete <id>")
        sys.exit()

    command = args[1]

    if command == "create_db":
        create_db()
    elif command == "add":
        add_drink(args[2], args[3])
    elif command == "list":
        list_drinks()
    elif command == "update":
        update_drink(int(args[2]), args[3], args[4])
    elif command == "delete":
        delete_drink(int(args[2]))
    else:
        print("Unknown command!!!")

import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


db_drop_and_create_all()

## ROUTES

@app.route('/drinks', methods=["GET"])
def get_drinks():
    drinks = Drink.query.all()
    drinksFormated = []
    for drink in drinks:
        drinksFormated.append(drink.short())
    
    print("passed")
    return jsonify({
      'success': True,
      'drinks': drinksFormated
    }), 200


@app.route('/drinks-detail', methods=["GET"])
@requires_auth('get:drinks-detail')
def get_drink_details(payload):
    drinks = Drink.query.all()
    drinksFormated = []
    for drink in drinks:
        drinksFormated.append(drink.long())
    
    print("passed2")
    return jsonify({
      'success': True,
      'drinks': drinksFormated
    }), 200


@app.route('/drinks', methods=["POST"])
@requires_auth('post:drinks')
def create_drink(payload):
    drink= Drink()
    try:
        body = request.get_json()
        title = body['title']
        print(body['recipe'])
        recipe = json.dumps(body['recipe'])
        if body== None or title == None or recipe== None:
            abort(404)

        drink = Drink(title=title,recipe=recipe)
        drink.insert() 
        print("passed3")
    except Exception as e:
        print(e)
        abort(422)

    return jsonify({
            'success': True,
            'drinks': drink.long()
        }), 200
    



@app.route('/drinks/<int:id>', methods=["PATCH"])
@requires_auth('patch:drinks')
def edit_drink(payload,id):
    drink= Drink()
    try:
        body = request.get_json()
        print(body)
        title = body['title']
        recipe = json.dumps(body['recipe'])
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if body== None or title == None or recipe== None or drink == None:
            abort(404)
        drink.title = title
        drink.recipe = recipe

        drink.update()
        print("passed4")

    except Exception as e:
        print(e)
        abort(422)

    return jsonify({
            'success': True,
            'drinks': drink.long()
        }), 200
    


@app.route('/drinks/<int:id>', methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(payload,id):
    drink= Drink()
    try:

        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink == None:
            abort(404)
        drink.delete()
        print("passed5")
        
    except Exception as e:
        print(e)
        abort(422)

    return jsonify({
            'success': True,
            'delete': id
        }), 200

## Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": error.status_code,
                    "message": error.error['description']
                    }), error.status_code
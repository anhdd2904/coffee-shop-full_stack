import os
from flask import Flask, request, jsonify, abort
from jose import jwt
from sqlalchemy import exc, text
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=['GET'])
@requires_auth('get:drinks')
def get_all_drink():
    drink_list = Drink.query.all()
    drinks = [d.short() for d in drink_list]
    return jsonify(
        {
            "success": True,
            "drinks": drinks
        }
    )


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks-detail", methods=['GET'])
@requires_auth('get:drinks-detail')
def get_all_drink_detail():
    drink_list = Drink.query.all()
    drinks = [d.long() for d in drink_list]
    return jsonify(
        {
            "success": True,
            "drinks": drinks
        }
    )


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=['POST'])
@requires_auth('post:drinks')
def save_drink():
    try:
        title = request.json['title']
        recipe = request.json['recipe']

        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()
        return jsonify({
            "success": True,
            "drinks": drink.long()
        })
    except Exception as e:
        print(e)
        return jsonify({
            "error": True
        })


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<id>", methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks_by_id(id):

    try:
        #id1 = text(id)
        drink_list = drink_exist(id)
        if drink_list is None:
            return jsonify({
                "error": True
            }),404
        drink1 = Drink.query.filter(Drink.id == id).one_or_none()
        drink1.title = request.json['title']
        drink1.update()
        return jsonify({
            "success": True,
            "drinks": drink1.long()
        })
    except Exception as e:
        print(e)
        return jsonify({
            "error": str(e)
        }),500


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<id>", methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink_by_id(id):

    try:
        #id1 = text(id)
        drink_list = drink_exist(id)
        if drink_list is None:
            return jsonify({
                "error": True
            }),404
        #drink = drink_list[0]
        drink_list.delete()
        return jsonify({
            "success": True,
            "drinks": drink_list.long()
        })
    except Exception as e:
        print(e)
        return jsonify({
            "error": str(e)
        }),500




def drink_exist(id):
    drink = Drink.query.get(id)
    print(drink)
    return drink

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404
'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify({
        "success": False,
        "error": e.status_code,
        "message": e.error['description']
    }), e.status_code

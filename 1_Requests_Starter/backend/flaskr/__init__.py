from audioop import cross
import json
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy  # , or_
from flask_cors import CORS
import random
from models import setup_db, Book


BOOKS_PER_SHELF = 4

def paginate_books(request, selection):
    """paginates the shows the number of items to display at a time"""
    page = request.args.get('page', 1, type=int)  # in case you want to show a specified number of items per page. 1st parameter gets the page number and if none is provided 2nd parameter is used by default
    start = (page - 1) * BOOKS_PER_SHELF # from index 0
    end = start + BOOKS_PER_SHELF
    formatted_books = [book.format() for book in selection]
    current_books = formatted_books[start:end]
    return current_books


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS,PATCH"
        )
        return response

    @app.route('/books')
    def get_books():
        """fetches all the books and paginate to return a specified number of books"""
        selection = Book.query.all()
        current_books = paginate_books(request, selection)
        if len(current_books) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'books':current_books,
            'total_books': len(Book.query.all())
        })

    app.route('/books/<int:book_id>', methods=['PATCH'])
    def update_book(book_id):

        body = request.get_json()

        try:
            book = Book.query.filter(Book.id==book_id)

            if book is None:
                abort(404)

            if "rating" in body:
                book.rating = int(body.get("rating"))

            book.update()
            
            return jsonify({
                "success": True, "id": book.id
                })

        except:
            abort(400)
    
    @app.route('/books/<int:book_id>', methods=['DELETE'])
    def delete_book(book_id):
        try:
            book = Book.query.filter(Book.id==book_id).first()
            if book is None:
                abort(404)
            book.delete()
            selection = Book.query.order_by(Book.id).all()
            current_books = paginate_books(request, selection)

            return jsonify({
                'success': True,
                'deleted': book_id,
                'books': current_books,
                'total_books': len(Book.query.all())
            })
        except LookupError:
            abort(442)

    @app.route("/books", methods=["POST"])
    def create_book():
        """creates a new entry"""
        # curl -X POST http://127.0.0.1:5000/books -H "Content-Type: application/json" -d '{"rating": "8", "author": "James Derrick", "title": "Home"}' - enter code into terminal
        body = request.get_json()

        new_title = body.get("title", None)
        new_author = body.get("author", None)
        new_rating = body.get("rating", None)

        try:
            book = Book(title=new_title, author=new_author, rating=new_rating)
            book.insert()

            selection = Book.query.order_by(Book.id).all()
            current_books = paginate_books(request, selection)

            return jsonify(
                {
                    "success": True,
                    "created": book.id,
                    "books": current_books,
                    "total_books": len(Book.query.all()),
                }
            )

        except:
            abort(422)

    @app.errorhandler(404)
    def not_found(error):
        """handles 404 errors"""
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "resource not found"
            }), 404
    

    @app.errorhandler(422)
    def unprocessable(error):
        """handles 422 errors"""
        return jsonify({
            "success": False, 
            "error": 422,
            "message": "server can't process request"
            }), 422

    
    @app.errorhandler(400)
    def invalid(error):
        """handles 400 errors"""
        return jsonify({
            "success": False, 
            "error": 400,
            "message": "invalid request"
            }), 400


    @app.errorhandler(405)
    def not_allowed(error):
        """handles 405 errors"""
        return jsonify({
            "success": False, 
            "error": 405,
            "message": "method not allowed"
            }), 405

    return app

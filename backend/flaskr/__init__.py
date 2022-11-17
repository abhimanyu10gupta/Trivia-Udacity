import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from flask_cors import CORS
import random


from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            categories = Category.query.all()
            category_ids = [category.id for category in categories]
            category_types = [category.type for category in categories]
            formatted_categories = {}
            for key in category_ids:
                for value in category_types:
                    formatted_categories[key] = value
                    category_types.remove(value)
                    break

            return jsonify({
                'status': True,
                'categories': formatted_categories,
                'total_categories': len(categories)
            })

        except:
            abort(405)

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE

            questions = Question.query.all()
            formatted_questions = [question.format() for question in questions]
            current_questions = formatted_questions[start:end]
            if len(current_questions) == 0:
                abort(404)
            categories = Category.query.all()
            category_ids = [category.id for category in categories]
            category_types = [category.type for category in categories]
            formatted_categories = {}
            for key in category_ids:
                for value in category_types:
                    formatted_categories[key] = value
                    category_types.remove(value)
                    break

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(formatted_questions),
                'current_category': None,
                'categories': formatted_categories,
            })
        except:
            abort(404)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            if question is None:
                abort(404)
            question.delete()

            return jsonify({
                'success': True,
                'deleted': question_id,
            })
        except:
            abort(404)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/newquestion', methods=['POST'])
    def submit_question():
        answer = request.json['answer']
        question = request.json['question']
        difficulty = request.json['difficulty']
        category = request.json['category']

        try:
            new_question = Question(
                question=question, answer=answer, category=category, difficulty=difficulty)
            new_question.insert()
            return jsonify({
                'success': True
            })
        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions', methods=['POST'])
    def search_questions():
        search_term = request.json['searchTerm']
        try:
            questions = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()
            formatted_questions = [question.format() for question in questions]
            return jsonify({
                'questions': formatted_questions,
                'total_questions': len(questions),
                'current_category': None
            })
        except:
            abort(404)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_category_questions(category_id):
        try:
            questions = Question.query.filter(
                Question.category == category_id).all()
            if len(questions) == 0:
                abort(404)
            formatted_questions = [question.format() for question in questions]
            print(questions)
            return jsonify({
                'questions': formatted_questions,
                'total_questions': len(questions),
                'current_category': category_id,
            })
        except:
            abort(404)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/quizzes', methods=['POST'])
    def get_next_questions():
        previous_questions = request.json['previous_questions']
        quiz_category = request.json['quiz_category']
        category_id = quiz_category['id']
        try:

            if category_id == 0:
                questions = Question.query.all()
                if len(previous_questions) == len(questions):
                    question = False
                else:
                    question = Question.query.filter(~Question.id.in_(
                        previous_questions)).order_by(func.random()).first().format()
            else:
                exists = Category.query.filter(
                    Category.id == category_id).one_or_none()
                if exists is None:
                    abort(404)
                questions = Question.query.filter(
                    Question.category == category_id).all()
                if len(previous_questions) == len(questions):
                    question = False
                else:
                    question = Question.query.filter(~Question.id.in_(
                        previous_questions), Question.category == category_id).order_by(func.random()).first().format()
            return jsonify({
                'previous_questions': previous_questions,
                'quiz_category': quiz_category,
                'question': question,
            })
        except:
            abort(404)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not Found"
        }), 404

    @app.errorhandler(422)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    @app.errorhandler(400)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Server Error"
        }), 500

    @app.errorhandler(405)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method Not Allowed"
        }), 405

    return app

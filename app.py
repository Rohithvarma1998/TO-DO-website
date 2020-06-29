from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/Todo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'

class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    todos = db.relationship('Todo',backref='list',lazy=True)

@app.route('/')
def index():
    return redirect(url_for('getTodos', list_id=1))

@app.route('/lists/<list_id>')
def getTodos(list_id):
    active_list = TodoList.query.get(list_id)
    lists = TodoList.query.order_by('id').all()
    items = Todo.query.filter_by(list_id = list_id).order_by('id').all()
    body = {'lists':lists,'items':items}
    return render_template('index.html', data = body, listId=active_list)

@app.route('/todos/create', methods=['POST'])
def create():
    error = False
    body={}
    try:
        todoDescription = request.get_json()['description']
        list_id = request.get_json()['list_id']
        todoItem = Todo(description=todoDescription, list_id = list_id)
        db.session.add(todoItem)
        db.session.commit()
        body['description'] = todoItem.description
        body['id'] = todoItem.id
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info)
    finally:
        db.session.close()
    if not error:
        return jsonify(body)
    else:
        abort(500)

@app.route('/todos/createList', methods=['POST'])
def createList():
    error = False
    body={}
    try:
        todoName = request.get_json()['name']
        todoListItem = TodoList(name=todoName)
        db.session.add(todoListItem)
        db.session.commit()
        body['name'] = todoListItem.name
        body['id'] = todoListItem.id
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info)
    finally:
        db.session.close()
    if not error:
        return jsonify(body)
    else:
        abort(500)

@app.route('/todos/complete', methods=['POST'])
def complete():
    error = False
    body = {}
    requestBody = request.get_json()
    try:
        todoId = int(requestBody['id'])
        todoItem = Todo.query.get(todoId)
        todoItem.completed = requestBody['completed']
        body['id'] = todoItem.id
        body['completed'] = todoItem.completed
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info)
    finally:
        db.session.close()
    if not error:
        return redirect(url_for("index"))

@app.route('/todos/<todoId>', methods=['DELETE'])
def delete(todoId):
    error = False
    try:
        todoItem = Todo.query.get(todoId)
        db.session.delete(todoItem)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info)
    finally:
        db.session.close()
    if not error:
        return jsonify({
            'success': True
        })


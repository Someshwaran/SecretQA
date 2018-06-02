from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import reqparse, abort, Api, Resource, fields, marshal
from datetime import datetime
from flask_heroku import Heroku

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#app.config['SQLALCHEMY_DATABASE_URI'] = 'oracle://system:secret@localhost:1521/xe'

api = Api(app)

heroku = Heroku(app)


db = SQLAlchemy(app)


todo_fields = {
    'todo_id': fields.Integer,
    'task': fields.String,
    'created_on': fields.DateTime()
}


class TodoData(db.Model):
    todo_id = db.Column(db.Integer, db.Sequence('todo_id_gen', start=1000, increment=2), primary_key=True)
    task = db.Column(db.Text)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


parser = reqparse.RequestParser()
parser.add_argument('task')

@app.route('/')
@app.route('/api')
@app.route('/api/')
def index():
    return "REST API for SecretQA"

class Todo(Resource):
    def get(self, tid):
        todo = TodoData.query.filter_by(todo_id=tid).first()
        if not todo:
            return {'status':0, 'message': 'Error', 'data': 'Todo with id {} not found'.format(tid)}
        return {'status':1, 'message': 'OK', 'data': marshal(todo, todo_fields)}

    def put(self, tid):
        todo = TodoData.query.filter_by(todo_id=tid).first()
        if not todo:
            return {'status':0, 'message': 'Error', 'data': 'Todo with id {} not found'.format(tid)}
        args = parser.parse_args()
        todo.task = args['task']
        db.session.add(todo)
        db.session.commit()
        return {'status':1, 'message': 'OK', 'data': marshal(todo, todo_fields)}
    
    def delete(self, tid):
        todo = TodoData.query.filter_by(todo_id=tid).first()
        if not todo:
            return {'status':0, 'message': 'Error', 'data': 'Todo with id {} not found'.format(tid)}
        db.session.delete(todo)
        db.session.commit()
        return {'status':1, 'message': 'OK', 'data': 'Todo with id {} deleted'.format(tid)}

class TodoList(Resource):

    def get(self):
        todos = TodoData.query.all()
        return {'status':1, 'message': 'OK', 'data': [marshal(todo, todo_fields) for todo in todos]}

    def post(self):
        args = parser.parse_args()
        todo = TodoData(task = args['task'])
        db.session.add(todo)
        db.session.commit()
        return {'status':1, 'message': 'OK', 'data': marshal(todo, todo_fields)}
    

api.add_resource(TodoList, '/api/todos', '/api/todos/')
api.add_resource(Todo, '/api/todos/<int:tid>', '/api/todos/<int:tid>/')



from flask import redirect, url_for

@app.route('/load/<pid>')
def handle_data(pid):
    return 'Data Id #{}'.format(pid)

@app.route('/red')
def change_resp():
    return redirect(url_for('handle_data', pid=10))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

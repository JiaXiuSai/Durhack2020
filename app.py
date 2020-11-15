from flask import Flask, render_template, request, redirect, url_for, session, g, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'redfestival'

def sort(list):
    table = {}

    for users in list:
        table[users.username] = users.score

    sorted_table = {k: v for k, v in sorted(table.items(), key=lambda item: item[1], reverse=True)}
    print(sorted_table)

    return sorted_table


@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./todo.db'
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    complete = db.Column(db.Boolean)
    posted_by = db.Column(db.String(50))

class User:
    def __init__(self, id, username, password, score):
        self.id = id
        self.username = username
        self.password = password
        self.score = score

    def __repr__(self):
        return f'<User: {self.username}>'


users = [User(id=1, username='Mac', password='password', score=0), User(id=2, username='Jisoo', password='password',score=0),
         User(id=3, username='Johnny', password='password', score=0)]

print(users[1].id)
sort(users)


@app.route('/')
def index():
    if not g.user:
        return redirect(url_for('login'))

    incomplete = Todo.query.filter_by(complete=False).filter_by(posted_by=g.user.username).all()
    completed = Todo.query.filter_by(complete=True).filter_by(posted_by=g.user.username).all()
    sorted_list = sort(users)
    print(sorted_list)
    return render_template('index.html', incomplete=incomplete, complete=completed, sorted_list=sorted_list)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)
        username = request.form['username']
        password = request.form['password']

        user = [x for x in users if x.username == username][0]
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('index'))

        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/add', methods=['POST'])
def add():
    posted = g.user.username
    todo = Todo(text=request.form['todoitem'], complete=False, posted_by=posted)
    db.session.add(todo)
    db.session.commit()

    return redirect(url_for('index'))


@app.route('/complete/<id>')
def complete(id):
    todo = Todo.query.filter_by(id=int(id)).first()
    todo.complete = True
    g.user.score += 1
    db.session.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
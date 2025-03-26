from flask import Flask, render_template, request
from sqlalchemy import create_engine, text

app = Flask(__name__)
conn_str = "mysql://root:cset155@localhost/exams"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/login.html')
def signUp():
    return render_template('login.html')

@app.route('/home.html')
def home():
    return render_template('home.html')

@app.route('/tests.html')
def tests():
    return render_template('tests.html')

@app.route('/accounts.html')
def accounts():
    accounts = conn.execute(text('select * from accounts')).all()
    return render_template('accounts.html', accounts = accounts[:10])

if __name__ == '__main__':
    app.run(debug=True)
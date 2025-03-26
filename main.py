from flask import Flask, render_template, request
from sqlalchemy import create_engine, text

app = Flask(__name__)
conn_str = "mysql://root:cset155@localhost/exams"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()

@app.route('/')
def hello():
    return render_template('base.html')

@app.route('/signup')
def signUp():
    return render_template('signup.html')

@app.route('/tests')
def tests():
    return render_template('tests.html')

@app.route('/accounts')
def accounts():
    return render_template('accounts.html')

if __name__ == '__main__':
    app.run(debug=True)
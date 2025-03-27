from flask import Flask, render_template, request
from sqlalchemy import create_engine, text

app = Flask(__name__)
conn_str = "mysql://root:cset155@localhost/exams"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()

@app.route('/', methods=["GET"])
def getAccounts():
    return render_template('index.html')

@app.route('/', methods=["POST"])
def signup():
    try:
        conn.execute(text('insert into accounts(Username, EmailAddress, UserPassword, AccountType) values(:Username, :EmailAddress, :UserPassword, :AccountType)'), request.form)
        conn.commit()
        return render_template('login.html', error = None, success = "Successful")
    except:
        return render_template('index.html', error = "Failed", success = None)

@app.route('/login.html')
def login():
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

'''
@app.route("/", method=["GET", "POST"])
def create_test():
    try: 
        conn.execute(text("Insert into tests (question_text) VALUES (:question_text)"),)
'''
    
if __name__ == '__main__':
    app.run(debug=True)
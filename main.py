from flask import Flask, render_template, request, redirect, flash
from sqlalchemy import create_engine, text
 
app = Flask(__name__)
conn_str = "mysql://root:cset155@localhost/exams"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()
app.secret_key = 'lunchFarts'

@app.route('/', methods=["GET"])
def getAccounts():
    return render_template('index.html')

@app.route('/', methods=["POST"])
def signup():
    try:
        conn.execute(text('insert into accounts(Username, EmailAddress, UserPassword, AccountType, IsLoggedIn) values(:Username, :EmailAddress, :UserPassword, :AccountType, 0)'), request.form)

        account_type = request.form.get("AccountType")
        account_id = conn.execute(text('select last_insert_id()')).scalar()

        if account_type == "Student":
            conn.execute(text('insert into students(AccountID, AccountType) values(:AccountID, :AccountType)'), {"AccountID": account_id, "AccountType": account_type})
        elif account_type == "Teacher":
            conn.execute(text('insert into teachers(AccountID, AccountType) values(:AccountID, :AccountType)'), {"AccountID": account_id, "AccountType": account_type})
            
        conn.commit()
        return render_template('login.html', error = None, success = "Successful")
    except:
        return render_template('index.html', error = "Failed", success = None)

@app.route('/login.html', methods=["GET"])
def getlogins():
    conn.execute(text('update accounts set IsLoggedIn = 0'))
    conn.commit()
    return render_template('login.html')

@app.route('/login.html', methods=["POST"])
def login():
    try:
        username = request.form.get("Username")
        print(username)
        password = request.form.get("UserPassword")
        print(password)
        query = conn.execute(text(f'select UserPassword from accounts where Username = :username'), {'username': username}).scalar()
        print(query)
        
        if query and password == query:
            conn.execute(text('update accounts set IsLoggedIn = 1 where Username = :username'),  {'username': username})
            conn.commit()
            return render_template('home.html', error = None, success = "Successful")
    except:
        return render_template('login.html', error = "Incorrect Username or Password", success = None)

@app.route('/home.html')
def home():
    return render_template('home.html')

@app.route('/accounts.html')
def accounts():
    account_type = request.args.get('AccountType', '')
    query = 'select * from accounts'

    if account_type:
        query += ' where AccountType = :AccountType'

    accounts = conn.execute(text(query), {"AccountType": account_type}).all() if account_type else conn.execute(text(query)).all()
    return render_template('accounts.html', accounts = accounts)

@app.route("/tests.html", methods=["Get"])
def gettests():
    return render_template('tests.html')

@app.route("/tests.html", methods=["POST", "GET"])
def create_test():
    try:
        conn.execute(text('Insert into tests(TestName, Question) values(:TestName, :Question)'), request.form)
        return render_template('tests.html', error = None, success = "Successful")
    except:
        return render_template('tests.html', error = "failed", succes = None)

if __name__ == '__main__':
    app.run(debug=True)
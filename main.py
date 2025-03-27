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
    
    return render_template('login.html')

@app.route('/login.html', methods=["POST"])
def login():
    try:
        password = conn.execute(text('select UserPassword from accounts')).fetchone()

        if password == request.form.get("UserPassword"):
            return render_template('login.html', error = None, success = "Successful")
    except:
        return render_template('login.html', error = "Failed", success = None)

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


@app.route("/", methods=["GET", "POST"])
def create_test():
    question_count = int(request.form.get('question_count', 1))

    if request.method == 'POST':
        if 'add_question' in request.form:
            question_count += 1
        elif 'submit_test' in request.form:
            test_name = request.form.get('testName')
            questions = [request.form.get(f'question{i}') for i in range(1, question_count + 1)]
            return f"Test Name: {test_name}, Questions: {questions}"
        
    return render_template('tests.html', question_count=question_count)

    
if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, url_for, redirect
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
        password = request.form.get("UserPassword")
        query = conn.execute(text(f'select UserPassword from accounts where Username = :username'), {'username': username}).scalar()
        
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

@app.route('/tests.html', methods=["GET","POST"])
def manage_tests():
    try:
        account_type = conn.execute(text('select AccountType from accounts where IsLoggedIn = 1')).scalar()
        test_name = request.form.get("test_name")
        description = request.form.get("description")
        questions = request.form.getlist("questions[]")
        account_id = conn.execute(text('select AccountID from accounts where IsLoggedIn = 1')).scalar()

        if test_name and description and questions:
            question_str = ','.join(questions)
            conn.execute(text('insert into tests(TestName, StudentCompletions, AccountID, Questions, Description) values(:test_name, 0, :account_id, :questions, :description)'), {"test_name": test_name, "account_id": account_id, "questions": question_str, "description": description})
            conn.commit()

        tests = conn.execute(text('select TestID, TestName, Description from tests')).fetchall()

        return render_template('tests.html', tests=tests, AccountType=account_type, error = None, success = "Successful")
    except:
        return render_template('tests.html', AccountType=account_type, error = "Failed", success = None)

@app.route("/take_test/<int:test_id>", methods=["GET", "POST"])
def take_test(test_id):
    account_id = conn.execute(text('select AccountID from accounts where IsLoggedIn = 1')).scalar()

    if request.method == "POST":
        responses = request.form.getlist("responses[]")

        responses_str = ",".join(responses)

        conn.execute(text('insert into responses (TestID, StudentID, ResponseText) values (:test_id, :student_id, :response_text)'), {"test_id": test_id, "student_id": account_id, "response_text": responses_str})
                    
        conn.execute(text(f'update tests set StudentCompletions = StudentCompletions + 1 where TestID = {test_id}'), {"test_id": test_id})

        conn.commit()

        return redirect(url_for("manage_tests"))


    test = conn.execute(text("select TestName, Questions from tests where TestID = :test_id"), {"test_id": test_id}).fetchone()
    
    if test:
        questions = test.Questions.split(",")
        return render_template("taketest.html", test_name=test.TestName, questions=questions)
    else:
        return render_template("home.html", error="Test not found.")
    
@app.route('/delete_test/<int:test_id>', methods=['POST'])
def delete_test(test_id):
    conn.execute(text('Delete from tests where TestID = :test_id'), {"test_id": test_id})
    conn.commit()
    return redirect(url_for("manage_tests"))

@app.route('/test_responses/<int:test_id>', methods=["GET", "POST"])
def see_responses(test_id):
    test = conn.execute(text("select TestName from tests where TestID = :test_id"), {"test_id": test_id}).fetchone()

    responses = conn.execute(text("select accounts.Username, responses.ResponseText from responses join accounts on responses.StudentID = accounts.AccountID where responses.TestID = :test_id"), {"test_id": test_id}).fetchall()

    if not test:
        return redirect(url_for("manage_tests"))
    
    return render_template("responses.html", test_name=test.TestName, responses=responses)

if __name__ == '__main__':
    app.run(debug=True)
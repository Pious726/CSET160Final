from flask import Flask, render_template, request, redirect
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
        username = request.form.get("Username")
        password = request.form.get("UserPassword")
        query = conn.execute(text(f'select UserPassword from accounts where Username = :username'), {'username': username}).scalar()
        
        if query and password == query:
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


@app.route("/tests.html", methods=["POST"])
def create_tests():
    try:
        TestName = request.form.get('TestName', '').strip()
        questions = [request.form.get(f'question{i}', '').strip() for i in range(1, int(request.form.get('question_count', '1')) + 1) if request.form.get(f'question{i}')]
    
        if TestName and questions:
            with engine.connect() as conn:
                conn.execute("insert into tests (TestName) values (:TestName)", {"TestName": TestName})
                TestID = conn.execute("select last_insert_id()").scalar()
                conn.execute(
                     "insert into questions (TestID, question_text) values (:TestID, :question_text)",
                    [{"TestID": TestID, "question_text": q} for q in questions]

                )
                conn.commit()
            return redirect("/tests.html")
    except:
        return render_template("tests.html", error="Submission failed")

@app.route("/tests.html", methods=["GET"])
def get_tests():
    with engine.connect() as conn:
        result = conn.execute("select TestID, TestName from tests")
        tests = result.fetchall()

        for test in tests:
            questions_result = conn.execute("Select question-text from questions where TestID = :TestID", {"TestID", test["id"]})
            test["questions"] = [row["question_text"] for row in questions_result.fetchall()]

    return render_template('tests.html', question_count=1, questions=[], TestName="", submitted_tests=tests)

if __name__ == '__main__':
    app.run(debug=True)
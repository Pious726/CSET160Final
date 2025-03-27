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
        password = request.form.get("UserPassword")
        username = request.form.get("Username")
        
        if password == conn.execute(text(f'select UserPassword from accounts where Username = {username}')).fetchone():
            return render_template('login.html', error = None, success = "Successful")
    except:
        return render_template('login.html', error = "Incorrect username or password", success = None)

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

@app.route("/tests.html", methods=["GET", "POST"])
def create_test():
    if request.method == "GET":
        question_count = 1
        questions = []
        test_name = ""
    else:
        # Get the current question count from the form
        question_count = request.form.get('question_count', '1')
        question_count = int(question_count) if question_count.isdigit() else 1

        # List to store the entered questions
        questions = []
        for i in range(1, question_count + 1):
            question = request.form.get(f'question{i}')
            if question:
                questions.append(question)

        # Retain the test name entered by the user
        test_name = request.form.get('testName', '')

        # If the "Add Question" button was clicked, increase question count
        if 'add_question' in request.form:
            question_count += 1
        # If the "Submit Test" button was clicked, show the submitted test data
        elif 'submit_test' in request.form:
            return f"Test Name: {test_name}, Questions: {questions}"

    return render_template('tests.html', question_count=question_count, questions=questions, test_name=test_name)

if __name__ == '__main__':
    app.run(debug=True)

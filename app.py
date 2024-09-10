from os import getenv
from flask import Flask
from flask import redirect, render_template, request, session, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from init_db import init_database, add_test_data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = getenv('SECRET_KEY')
env = getenv('FLASK_ENV')

#### ENDPOINT ONLY FOR INITIALIZING DB - THIS WILL REPLACE ALL DATA IN TABLES ####
@app.route('/init_db')
def init_db():
    print(env)
    if env != 'develop':
        return Response('', 404)
    init_database(db)
    add_test_data(db)
    return Response('All good', 200)

#### Landing page ####
@app.route('/')
def index():
    programs = []
    if 'username' in session:
        result = db.session.execute(
            text('SELECT id, name FROM programs WHERE user_id = :user_id'),
            {'user_id': session['user_id']}
        )
        programs = result.fetchall()
    return render_template('index.html', programs=programs)

#### AUTH ####
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    result = db.session.execute(
        text('SELECT id, pwhash FROM users WHERE username = :username'),
        {'username':username}
    )
    resultArr = result.fetchone()
    if resultArr and len(resultArr)>0:
        user_id = resultArr[0]
        pwhash = resultArr[1]
        if check_password_hash(pwhash=pwhash, password=password):
            session['username'] = username
            session['user_id'] = user_id
    return redirect('/')

@app.route('/logout')
def logout():
    if 'username' in session:
        del session['username']
    return redirect('/')


#### USER CREATION ####
@app.route('/create-user')
def create_user():
    if 'username' in session:
        return redirect('/')
    return render_template('create-user.html')

@app.route('/api/create-user', methods=['POST'])
def create_user_api():
    if 'username' in session:
        return redirect('/')
    username = request.form['username']
    password = request.form['password']

    # Using different less secure method here because macOS doesn't come with openSSL
    hash_value = generate_password_hash(password, method='pbkdf2')
    sql = text('INSERT INTO users (username, pwhash) VALUES (:username, :pwhash) RETURNING id')
    result = db.session.execute(sql, {'username':username, 'pwhash':hash_value})
    db.session.commit()
    user_id = result.fetchone()[0]
    session['username'] = username
    session['user_id'] = user_id
    return redirect('/')


#### PROGRAM ENDPOINTS ####
@app.route('/create-program')
def create_program():
    if 'username' not in session:
        return redirect('/')
    print(session)
    return render_template('create-new-program.html')

@app.route('/api/create-program', methods=['POST'])
def create_program_api():
    if 'username' not in session:
        return redirect('/')
    name = request.form['programName']
    result = db.session.execute(
        text('INSERT INTO programs (name, user_id) VALUES (:name, :user_id) RETURNING id'),
        {'name':name, 'user_id': session['user_id']}
    )
    poll_id = result.fetchone()[0]
    db.session.commit()
    return redirect('/edit-program/'+str(poll_id))

@app.route('/edit-program/<int:id>')
def edit_program(id):
    if 'username' not in session:
        return redirect('/')
    result = db.session.execute(
        text('SELECT id, name FROM programs WHERE id = :id AND user_id = :user_id'),
        {'id':id, 'user_id': session['user_id']}
    )
    program = result.fetchone()
    result = db.session.execute(
        text('SELECT id, name, sets, reps FROM exercises WHERE program_id = :id AND user_id = :user_id'),
        {'id':id, 'user_id': session['user_id']}
    )
    exercises = result.fetchall()
    result = db.session.execute(
        text('SELECT id, name FROM templates WHERE user_id = :user_id OR user_id is NULL'),
        {'id':id, 'user_id': session['user_id']}
    )
    templates = result.fetchall()
    if not program or len(program) < 1:
        return redirect('/')
    return render_template('edit-program.html', program_name=program[1], program_id=id, exercises=exercises, templates=templates)

@app.route('/edit-program/<int:id>/edit')
def edit_program_name(id):
    if 'username' not in session:
        return redirect('/')
    result = db.session.execute(
        text('SELECT id, name FROM programs WHERE id = :id AND user_id = :user_id'),
        {'id':id, 'user_id': session['user_id']}
    )
    program = result.fetchone()
    if not program or len(program) < 1:
        return redirect('/')
    return render_template('edit-program-name.html', program_name=program[1], program_id=id)

@app.route('/edit-program/<int:id>/save', methods=['POST'])
def save_program_name(id):
    if 'username' not in session:
        return redirect('/')
    name = request.form['name']
    db.session.execute(
        text('UPDATE programs SET name=:name WHERE id = :id AND user_id = :user_id'),
        {'name':name, 'id':id, 'user_id': session['user_id']}
    )
    db.session.commit()
    return redirect('/edit-program/'+str(id))

@app.route('/add-exercise', methods=['POST'])
def add_exercise():
    if 'username' not in session:
        return redirect('/')
    name = request.form['exercise_name']
    sets = request.form['exercise_sets']
    reps = request.form['exercise_reps']
    program_id = request.form['program_id']
    # Validate that program belongs to the user.
    # If not just redirect back to program without deleting.
    result = db.session.execute(
        text('SELECT id, name FROM programs WHERE id = :id AND user_id = :user_id'),
        {'id':program_id, 'user_id': session['user_id']}
    )
    program = result.fetchone()
    if program:
        db.session.execute(
            text('INSERT INTO exercises (name, reps, sets, program_id, user_id) \
                VALUES (:name, :reps, :sets, :program_id, :user_id) \
                RETURNING id'),
            {
                'name': name,
                'sets': sets,
                'reps': reps,
                'program_id': program_id,
                'user_id': session['user_id'],
            }
        )
        db.session.commit()

    return redirect('/edit-program/' + str(program_id))

@app.route('/delete_exercise/<int:id>', methods=['DELETE'])
def remove_exercise(id):
    if 'username' not in session:
        return redirect('/')

    db.session.execute(
        text('DELETE FROM exercises WHERE id = :id AND user_id = :user_id'),
        {
            'id': id,
            'user_id': session['user_id']
        }
    )
    db.session.commit()
    return Response('', 204)

@app.route('/update-exercise/<int:id>', methods=['POST'])
def update_exercise(id):
    if 'username' not in session:
        return redirect('/')
    name = request.form['exercise_name']
    sets = request.form['exercise_sets']
    reps = request.form['exercise_reps']
    program_id = request.form['program_id']
    # validate that program belongs to the user.
    # If not just redirect back to program without deleting.
    result = db.session.execute(
        text('SELECT id, name FROM programs WHERE id = :id AND user_id = :user_id'),
        {'id':program_id, 'user_id': session['user_id']}
    )
    program = result.fetchone()
    if program:
        db.session.execute(
            text(
                """
                    UPDATE exercises SET name=:name, reps=:reps, sets=:sets 
                    WHERE id=:id AND program_id=:program_id AND user_id=user_id
                """
            ),
            {
                'id': id,
                'name': name,
                'sets': sets,
                'reps': reps,
                'program_id': program_id,
                'user_id': session['user_id'] 
            }
        )
        db.session.commit()
    return redirect('/edit-program/' + str(program_id))

#### RESULTS ####
@app.route('/results/<int:id>')
def results(id):
    if 'username' not in session:
        return redirect('/')

    result = db.session.execute(
        text(
            """
                SELECT rs.date, e.name, r.result, rs.id
                FROM resultsets rs
                LEFT JOIN results r on rs.id = r.resultset
                LEFT JOIN exercises e on r.exercise_id = e.id
                WHERE rs.program_id = :id AND rs.user_id = :user_id
            """
        ),
        {'id':id, 'user_id': session['user_id']}
    )
    results = result.fetchall()
    return render_template('results.html', results=results, program_id=id)

@app.route('/results/<int:id>/add')
def add_result(id):
    if 'username' not in session:
        return redirect('/')
    result = db.session.execute(
        text('SELECT id, name FROM programs WHERE id = :id AND user_id = :user_id'),
        {'id':id, 'user_id': session['user_id']}
    )
    program = result.fetchone()
    result = db.session.execute(
        text('SELECT id, name, sets, reps FROM exercises WHERE program_id = :id AND user_id = :user_id'),
        {'id':id, 'user_id': session['user_id']}
    )
    exercises = result.fetchall()
    return render_template('add-result.html', program=program, exercises=exercises)

@app.route('/results/<int:id>/save', methods=["POST"])
def save_result(id):
    if 'username' not in session:
        return redirect('/')
    print(request.form)

    # validate that program belongs to the user.
    # If not just redirect back to program without deleting.
    result = db.session.execute(
        text('SELECT id, name FROM programs WHERE id = :id AND user_id = :user_id'),
        {'id':id, 'user_id': session['user_id']}
    )
    program = result.fetchone()
    if program:
        result = db.session.execute(
                text('INSERT INTO resultsets (program_id, user_id, date) \
                    VALUES (:program_id, :user_id, :date) \
                    RETURNING id'),
                {
                    'program_id': id,
                    'user_id': session['user_id'],
                    'date': '2022-01-01'
                }
            )
        db.session.commit()
        resultset_id = result.fetchone()[0]
        for exercise in request.form:
            if exercise.isnumeric() and request.form[exercise].isnumeric():
                db.session.execute(
                        text('INSERT INTO results (resultset, exercise_id, result) \
                            VALUES (:resultset, :exercise_id, :result) \
                            RETURNING id'),
                        {
                            'resultset': resultset_id,
                            'exercise_id': int(exercise),
                            'result': int(request.form[exercise])
                        }
                    )
                db.session.commit()

    
    return redirect('/results/'+str(id))
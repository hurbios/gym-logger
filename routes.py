from os import getenv
from flask import redirect, render_template, request, session, Response

from app import app
from init_db import init_database, add_test_data
import programs
import users
import exercises
import results
import utils

env = getenv('FLASK_ENV')

#### ENDPOINT ONLY FOR INITIALIZING DB - THIS WILL REPLACE ALL DATA IN TABLES ####
@app.route('/init_db')
def init_db():
    if env != 'develop':
        return Response('', 404)
    init_database()
    add_test_data()
    return Response('All good', 200)

#### Landing page ####
@app.route('/')
def index():
    programs_list = []
    if 'username' in session:
        programs_list = programs.get_programs()
    return render_template('index.html', programs=programs_list)

#### USER ROUTES ####
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    users.login(username, password)
    return redirect('/')

@app.route('/logout')
def logout():
    users.logout()
    return redirect('/')

@app.route('/register', methods=["GET", "POST"])
def register():
    if 'username' in session:
        return redirect('/')
    if request.method == "GET":
        return render_template('register.html')
    else:
        # TODO CSRF?
        username = request.form['username']
        password = request.form['password']
        users.register(username, password)
        return redirect('/')

#### PROGRAM ENDPOINTS ####
@app.route('/create-program', methods=["GET", "POST"])
def create_program():
    if 'username' not in session:
        return redirect('/')
    if request.method == "GET":
        return render_template('create-new-program.html')
    else:
        if utils.check_csrf_token(request.form):
            return Response("Invalid CSRF token", 403)
        name = request.form['programName']
        program_id = programs.create_program(name)
        return redirect('/edit-program/'+str(program_id))

@app.route('/edit-program/<int:id>')
def edit_program(id):
    if 'username' not in session:
        return redirect('/')
    program = programs.get_program(id)
    if not program or len(program) < 1:
        return redirect('/')
    program_exercises = exercises.get_program_exercises(id)
    templates = exercises.get_exercise_templates(id)
    return render_template(
        'edit-program.html',
        program_name=program[1],
        program_id=id,
        exercises=program_exercises,
        templates=templates
    )

@app.route('/edit-program/<int:id>/edit', methods=["GET","POST"])
def edit_program_name(id):
    if 'username' not in session:
        return redirect('/')

    if request.method == "GET":
        program = programs.get_program(id)
        if not program or len(program) < 1:
            return redirect('/')
        return render_template('edit-program-name.html', program_name=program[1], program_id=id)
    else:
        if utils.check_csrf_token(request.form):
            return Response("Invalid CSRF token", 403)
        name = request.form['name']
        programs.change_program_name(id, name)
        return redirect('/edit-program/'+str(id))   

#### EXERCISE ENDPOINTS ####
@app.route('/add-exercise', methods=['POST'])
def add_exercise():
    if 'username' not in session:
        return redirect('/')
    if utils.check_csrf_token(request.form):
        return Response("Invalid CSRF token", 403)
    name = request.form['exercise_name']
    sets = request.form['exercise_sets']
    reps = request.form['exercise_reps']
    program_id = request.form['program_id']
    # Validate that program belongs to the user.
    program = programs.get_program(program_id)
    if program:
        exercises.add_exercise(name, sets, reps, program_id)
    return redirect('/edit-program/' + str(program_id))

@app.route('/delete_exercise/<int:id>', methods=['DELETE'])
def remove_exercise(id):
    if 'username' not in session:
        return redirect('/')
    if utils.check_csrf_token(request.form):
        return Response("Invalid CSRF token", 403)
    exercises.delete_exercise(id)
    return Response('', 204)

@app.route('/update-exercise/<int:id>', methods=['POST'])
def update_exercise(id):
    if 'username' not in session:
        return redirect('/')
    if utils.check_csrf_token(request.form):
        return Response("Invalid CSRF token", 403)
    name = request.form['exercise_name']
    sets = request.form['exercise_sets']
    reps = request.form['exercise_reps']
    program_id = request.form['program_id']
    # Validate that program belongs to the user.
    program = programs.get_program(program_id)
    if program:
        exercises.update_exercise(id, name, sets, reps, program_id)
    return redirect('/edit-program/' + str(program_id))

#### RESULTS ####
@app.route('/results/<int:id>')
def show_results(id):
    if 'username' not in session:
        return redirect('/')
    results_list = results.get_results(id)
    return render_template('results.html', results=results_list, program_id=id)

@app.route('/results/<int:id>/add')
def add_result(id):
    if 'username' not in session:
        return redirect('/')
    program = programs.get_program(id)
    exercise_list = exercises.get_program_exercises(id)
    return render_template('add-result.html', program=program, exercises=exercise_list)

@app.route('/results/<int:id>/save', methods=["POST"])
def save_result(id):
    if 'username' not in session:
        return redirect('/')
    if utils.check_csrf_token(request.form):
        return Response("Invalid CSRF token", 403)
    # validate that program belongs to the user.
    program = programs.get_program(id)
    if program:
        results.add_result_set(id, request.form)
    return redirect('/results/'+str(id))

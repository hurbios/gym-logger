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
    username = request.form.get('username')
    password = request.form.get('password')
    if not utils.validate_all([username, password]):
        return Response('Incorrect input', 400)
    users.login(username, password)
    return redirect('/')

@app.route('/logout')
def logout():
    users.logout()
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect('/')
    if request.method == 'GET':
        return render_template('register.html')
    else:
        # TODO CSRF?
        username = request.form.get('username')
        password = request.form.get('password')
        if not utils.validate_all([username, password]):
            return Response('Incorrect input', 400)
        users.register(username, password)
        return redirect('/')

#### PROGRAM ENDPOINTS ####
@app.route('/create-program', methods=['GET', 'POST'])
def create_program():
    if 'username' not in session:
        return redirect('/')
    if request.method == 'GET':
        return render_template('create-new-program.html')
    else:
        if utils.check_csrf_token(request.form):
            return Response('Invalid CSRF token', 403)
        name = utils.validate(request.form.get('programName'), 'string')
        program_id = programs.create_program(name)
        return redirect('/edit-program/'+str(program_id))

@app.route('/edit-program/<int:id>')
def edit_program(id):
    if 'username' not in session:
        return redirect('/')
    if not utils.validate(id, 'number'):
        return Response('Incorrect program ID', 400)
    program = programs.get_program(id)
    if not program or len(program) < 1:
        return redirect('/')
    program_exercises = exercises.get_program_exercises(id)
    templates = exercises.get_exercise_templates(id)
    has_results = results.program_has_results(id)
    return render_template(
        'edit-program.html',
        program_name=program[1],
        program_id=id,
        exercises=program_exercises,
        templates=templates,
        has_results=has_results
    )

@app.route('/edit-program/<int:id>/edit', methods=['GET', 'POST'])
def edit_program_name(id):
    if 'username' not in session:
        return redirect('/')
    if not utils.validate(id, 'number'):
        return Response('Incorrect program ID', 400)
    if request.method == 'GET':
        program = programs.get_program(id)
        if not program or len(program) < 2:
            return redirect('/')
        return render_template('edit-program-name.html', program_name=program[1], program_id=id)
    else:
        if utils.check_csrf_token(request.form):
            return Response('Invalid CSRF token', 403)
        name = request.form.get('name')
        programs.change_program_name(id, name)
        return redirect('/edit-program/'+str(id))   

#### EXERCISE ENDPOINTS ####
@app.route('/add-exercise', methods=['POST'])
def add_exercise():
    if 'username' not in session:
        return redirect('/')
    if utils.check_csrf_token(request.form):
        return Response('Invalid CSRF token', 403)
    name = request.form.get('exercise_name')
    sets = request.form.get('exercise_sets')
    reps = request.form.get('exercise_reps')
    program_id = request.form.get('program_id')
    if not utils.validate_all([name], [sets, reps, program_id]):
        return Response('Incorrect input', 400)
    # Validate that program belongs to the user.
    if programs.get_program(program_id) and not results.program_has_results(program_id):
        exercises.add_exercise(name, sets, reps, program_id)
    return redirect('/edit-program/' + str(program_id))

@app.route('/delete_exercise/<int:id>', methods=['DELETE'])
def remove_exercise(id):
    if 'username' not in session:
        return redirect('/')
    if utils.check_csrf_token(request.form):
        return Response('Invalid CSRF token', 403)
    if not utils.validate(id, 'number'):
        return Response('Incorrect program ID', 400)
    if results.program_has_results(exercises.get_program_id_with_exercise_id(id)):
        return Response('Program with results cannot be edited', 400)
    exercises.delete_exercise(id)
    return Response('', 204)

@app.route('/update-exercise/<int:id>', methods=['POST'])
def update_exercise(id):
    if 'username' not in session:
        return redirect('/')
    if utils.check_csrf_token(request.form):
        return Response('Invalid CSRF token', 403)
    name = request.form.get('exercise_name')
    sets = request.form.get('exercise_sets')
    reps = request.form.get('exercise_reps')
    program_id = request.form.get('program_id')
    if not utils.validate_all([name], [sets, reps, program_id, id]):
        return Response('Incorrect input', 400)
    # Validate that program belongs to the user.
    if programs.get_program(program_id) and not results.program_has_results(program_id):
        exercises.update_exercise(id, name, sets, reps, program_id)
    return redirect('/edit-program/' + str(program_id))

#### RESULTS ####
@app.route('/results/<int:id>')
def show_results(id):
    if 'username' not in session:
        return redirect('/')
    if not utils.validate(id, 'number'):
        return Response('Incorrect program ID', 400)
    results_list = results.get_results(id)
    return render_template('results.html', results=results_list, program_id=id)

@app.route('/results/<int:id>/add')
def add_result(id):
    if 'username' not in session:
        return redirect('/')
    if not utils.validate(id, 'number'):
        return Response('Incorrect program ID', 400)
    program = programs.get_program(id)
    exercise_list = exercises.get_program_exercises(id)
    return render_template('add-result.html', program=program, exercises=exercise_list)

@app.route('/results/<int:id>/save', methods=['POST'])
def save_result(id):
    if 'username' not in session:
        return redirect('/')
    if utils.check_csrf_token(request.form):
        return Response('Invalid CSRF token', 403)
    if not utils.validate(id, 'number'):
        return Response('Incorrect program ID', 400)
    # validate that program belongs to the user.
    if programs.get_program(id):
        results.add_result_set(id, request.form)
    return redirect('/results/'+str(id))

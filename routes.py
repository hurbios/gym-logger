from os import getenv
from flask import redirect, render_template, request, session, Response, abort

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

#### Error handlers ####
@app.errorhandler(400)
def error(e):
    return render_template('error.html',
                           description=e.description.get('message'),
                           url=e.description.get('url'))

#### Landing page ####
@app.route('/')
def index():
    programs_list = []
    err_message = session['err_message']
    session['err_message'] = None
    if 'username' in session:
        programs_list = programs.get_programs()
    return render_template('index.html', programs=programs_list, err_message=err_message)

#### USER ROUTES ####
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if not utils.validate_all([username, password], []):
        return Response('Incorrect input', 400)
    users.login(username, password)
    if 'username' not in session:
        session['err_message'] = 'Invalid credentials. Please try again.'
        return redirect('/')
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
    username = request.form.get('username')
    password = request.form.get('password')
    if not utils.validate_all([username, password], []):
        return Response('Incorrect input', 400)
    if not users.register(username, password):
        abort(400, { 'message': 'username is taken', 'url': '/register' })
    return redirect('/')

#### PROGRAM ENDPOINTS ####
@app.route('/create-program', methods=['GET', 'POST'])
def create_program():
    if 'username' not in session:
        return redirect('/')
    if request.method == 'GET':
        users.regenerate_csrf()
        return render_template('create-new-program.html')
    if utils.check_csrf_token(request.form):
        return Response('Invalid CSRF token', 403)
    name = request.form.get('program_name')
    description = request.form.get('description')
    if not utils.validate_all([name, description], []):
        return Response('Invalid input', 400)
    program_id = programs.create_program(name, description)
    if not program_id:
        abort(400, { 'message': 'Program could not be created' })
    return redirect('/edit-program/'+str(program_id))

@app.route('/edit-program/<int:id_>')
def edit_program(id_):
    if 'username' not in session:
        return redirect('/')
    if not utils.validate(id_, 'number'):
        return Response('Incorrect program ID', 400)
    program = programs.get_program(id_)
    if not program or len(program) < 1:
        return redirect('/')
    program_exercises = exercises.get_program_exercises(id_)
    has_results = results.program_has_results(id_)
    users.regenerate_csrf()
    return render_template(
        'edit-program.html',
        program_name=program[1],
        description=program[2],
        program_id=id_,
        exercises=program_exercises,
        has_results=has_results
    )

@app.route('/edit-program/<int:id_>/edit', methods=['GET', 'POST'])
def update_program(id_):
    if 'username' not in session:
        return redirect('/')
    if not utils.validate(id_, 'number'):
        return Response('Incorrect program ID', 400)
    if request.method == 'GET':
        program = programs.get_program(id_)
        if not program or len(program) < 2:
            return redirect('/')
        users.regenerate_csrf()
        return render_template('edit-program-name.html',
                               program_name=program[1],
                               description=program[2],
                               program_id=id_)
    if utils.check_csrf_token(request.form):
        return Response('Invalid CSRF token', 403)
    name = request.form.get('name')
    description = request.form.get('description')
    if not utils.validate_all([name, description], []):
        abort(400, { 'message': 'Invalid input', 'url': '/edit-program/' + id_ + '/edit' })
    if not programs.update_program(id_, name, description):
        abort(400, { 'message': 'Program could not be updated' })
    return redirect('/edit-program/'+str(id_))

@app.route('/delete_program/<int:id_>', methods=['DELETE'])
def remove_program(id_):
    if 'username' not in session:
        return redirect('/')
    if utils.check_csrf_token(request.args):
        return Response('Invalid CSRF token', 403)
    if not utils.validate(id_, 'number'):
        return Response('Incorrect program ID', 400)
    if not programs.get_program(id_):
        return Response('Program with results cannot be edited', 400)
    if not programs.delete_program(id_):
        abort(400, { 'message': 'Program could not be deleted' })
    users.regenerate_csrf()
    return Response('', 204)

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
        if exercises.add_exercise(name, sets, reps, program_id):
            users.regenerate_csrf()
            return redirect('/edit-program/' + str(program_id))
    abort(400, { 'message': 'Exercise could not be added' })

@app.route('/delete_exercise/<int:id_>', methods=['DELETE'])
def remove_exercise(id_):
    if 'username' not in session:
        return redirect('/')
    if utils.check_csrf_token(request.args):
        return Response('Invalid CSRF token', 403)
    if not utils.validate(id_, 'number'):
        return Response('Incorrect program ID', 400)
    if results.program_has_results(exercises.get_program_id_with_exercise_id(id_)):
        return Response('Program with results cannot be edited', 400)
    if not exercises.delete_exercise(id_):
        return Response('Program with results cannot be edited', 400)
    users.regenerate_csrf()
    return Response('', 204)

@app.route('/update-exercise/<int:id_>', methods=['POST'])
def update_exercise(id_):
    if 'username' not in session:
        return redirect('/')
    if utils.check_csrf_token(request.form):
        return Response('Invalid CSRF token', 403)
    name = request.form.get('exercise_name')
    sets = request.form.get('exercise_sets')
    reps = request.form.get('exercise_reps')
    program_id = request.form.get('program_id')
    if not utils.validate_all([name], [sets, reps, program_id, id_]):
        return Response('Incorrect input', 400)
    # Validate that program belongs to the user.
    if programs.get_program(program_id) and not results.program_has_results(program_id):
        if not exercises.update_exercise(id_, name, sets, reps, program_id):
            abort(400, { 'message': 'Exercise could not be updated' })
    users.regenerate_csrf()
    return redirect('/edit-program/' + str(program_id))

#### RESULTS ####
@app.route('/results/<int:id_>')
def show_results(id_):
    if 'username' not in session:
        return redirect('/')
    if not utils.validate(id_, 'number'):
        return Response('Incorrect program ID', 400)
    program = programs.get_program(id_)
    if not program or len(program) < 1:
        return redirect('/')
    results_list = results.get_results(id_)
    exercises_list = exercises.get_program_exercises(id_)
    results_by_id = {}
    for result in results_list:
        if result.id not in results_by_id:
            results_by_id[result.id] = {}
        if 'results' not in results_by_id[result.id]:
            results_by_id[result.id]['results'] = {}
        results_by_id[result.id]['results'][result.eid] = result.result
        if 'date' not in results_by_id[result.id]:
            results_by_id[result.id]['date'] = result.date
    users.regenerate_csrf()
    return render_template('results.html',
                           results=results_by_id,
                           program=program,
                           exercises=exercises_list)

@app.route('/results/<int:id_>/add')
def add_result(id_):
    if 'username' not in session:
        return redirect('/')
    if not utils.validate(id_, 'number'):
        return Response('Incorrect program ID', 400)
    program = programs.get_program(id_)
    exercise_list = exercises.get_program_exercises(id_)
    users.regenerate_csrf()
    return render_template('add-result.html', program=program, exercises=exercise_list)

@app.route('/results/<int:id_>/save', methods=['POST'])
def save_result(id_):
    if 'username' not in session:
        return redirect('/')
    if utils.check_csrf_token(request.form):
        return Response('Invalid CSRF token', 403)
    if not utils.validate(id_, 'number'):
        return Response('Incorrect program ID', 400)
    if not utils.validate(request.form.get('date'), 'date'):
        return Response('Invalid date', 400)
    # validate that program belongs to the user.
    if programs.get_program(id_):
        if not results.add_result_set(id_, request.form):
            abort(400, { 'message': 'Resultset could not be saved' })
    users.regenerate_csrf()
    return redirect('/results/'+str(id_))

@app.route('/results/<int:program_id>/delete/<int:id_>', methods=['DELETE'])
def delete_result(program_id,id_):
    if 'username' not in session:
        return redirect('/')
    if utils.check_csrf_token(request.args):
        return Response('Invalid CSRF token', 403)
    if not utils.validate_all([],[program_id, id_]):
        return Response('Incorrect program ID or resultset ID', 400)
    # validate that resultset belongs to the user.
    if not results.resultset_exists(id_):
        return Response('Incorrect resultset ID', 400)
    if not results.delete_resultset(id_):
        return Response('Resultset could not be deleted', 400)
    users.regenerate_csrf()
    return Response('', 204)

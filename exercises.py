from db import db
from flask import session
from sqlalchemy.sql import text

def get_program_exercises(id):
    try:
        result = db.session.execute(
            text('SELECT id, name, sets, reps FROM exercises WHERE program_id = :id AND user_id = :user_id'),
            {'id':id, 'user_id': session['user_id']}
        )
        return result.fetchall()
    except:
        return False


def get_exercise_templates(id):
    try:
        result = db.session.execute(
            text('SELECT id, name FROM templates WHERE user_id = :user_id OR user_id is NULL'),
            {'id':id, 'user_id': session['user_id']}
        )
        return result.fetchall()
    except:
        return False


def add_exercise(name, sets, reps, program_id):
    try:
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
        return True
    except:
        return False


def delete_exercise(id):
    try:
        db.session.execute(
            text('DELETE FROM exercises WHERE id = :id AND user_id = :user_id'),
            {
                'id': id,
                'user_id': session['user_id']
            }
        )
        db.session.commit()
        return True
    except:
        return False

def update_exercise(id, name, sets, reps, program_id):
    try:
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
        return True
    except:
        return False

def get_program_id_with_exercise_id(id):
    try:
        result = db.session.execute(
            text('SELECT program_id FROM exercises WHERE id = :id AND user_id = :user_id'),
            {'id':id, 'user_id': session['user_id']}
        )
        return result.fetchone()[0]
    except:
        return False

def delete_program_exercises(program_id):
    try:
        db.session.execute(
            text(
                """
                    DELETE
                    FROM exercises 
                    WHERE program_id = :program_id AND user_id = :user_id
                """
            ),
            {'program_id':program_id, 'user_id': session['user_id']}
        )
        db.session.commit()
        return True
    except:
        return False

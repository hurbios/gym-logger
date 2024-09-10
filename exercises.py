from db import db
from flask import session
from sqlalchemy.sql import text

def get_program_exercises(id):
    result = db.session.execute(
        text('SELECT id, name, sets, reps FROM exercises WHERE program_id = :id AND user_id = :user_id'),
        {'id':id, 'user_id': session['user_id']}
    )
    return result.fetchall()


def get_exercise_templates(id):
    result = db.session.execute(
        text('SELECT id, name FROM templates WHERE user_id = :user_id OR user_id is NULL'),
        {'id':id, 'user_id': session['user_id']}
    )
    return result.fetchall()


def add_exercise(name, sets, reps, program_id):
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


def delete_exercise(id):
    db.session.execute(
        text('DELETE FROM exercises WHERE id = :id AND user_id = :user_id'),
        {
            'id': id,
            'user_id': session['user_id']
        }
    )
    db.session.commit()


def update_exercise(id, name, sets, reps, program_id):
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

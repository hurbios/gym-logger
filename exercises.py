from flask import session
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from db import db

def get_program_exercises(id_):
    try:
        result = db.session.execute(
            text("""
                 SELECT id, name, sets, reps 
                 FROM exercises 
                 WHERE program_id = :id AND user_id = :user_id
            """),
            {'id':id_, 'user_id': session['user_id']}
        )
        return result.fetchall()
    except SQLAlchemyError:
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
    except SQLAlchemyError:
        return False


def delete_exercise(id_):
    try:
        db.session.execute(
            text('DELETE FROM exercises WHERE id = :id AND user_id = :user_id'),
            {
                'id': id_,
                'user_id': session['user_id']
            }
        )
        db.session.commit()
        return True
    except SQLAlchemyError:
        return False

def update_exercise(id_, name, sets, reps, program_id):
    try:
        db.session.execute(
            text(
                """
                    UPDATE exercises SET name=:name, reps=:reps, sets=:sets 
                    WHERE id=:id AND program_id=:program_id AND user_id=user_id
                """
            ),
            {
                'id': id_,
                'name': name,
                'sets': sets,
                'reps': reps,
                'program_id': program_id,
                'user_id': session['user_id'] 
            }
        )
        db.session.commit()
        return True
    except SQLAlchemyError:
        return False

def get_program_id_with_exercise_id(id_):
    try:
        result = db.session.execute(
            text('SELECT program_id FROM exercises WHERE id = :id AND user_id = :user_id'),
            {'id':id_, 'user_id': session['user_id']}
        )
        return result.fetchone()[0]
    except SQLAlchemyError:
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
    except SQLAlchemyError:
        return False

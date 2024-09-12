from db import db
from flask import session
from sqlalchemy.sql import text
import utils


def get_results(program_id):
    result = db.session.execute(
        text(
            """
                SELECT rs.date, e.name, r.result, rs.id
                FROM resultsets rs
                LEFT JOIN results r on rs.id = r.resultset
                LEFT JOIN exercises e on r.exercise_id = e.id
                WHERE rs.program_id = :program_id AND rs.user_id = :user_id
            """
        ),
        {'program_id':program_id, 'user_id': session['user_id']}
    )
    return result.fetchall()


def add_result_set(id, exercise_list):
    if not exercise_list or len(exercise_list) < 1:
        return
    should_commit = False
    result = db.session.execute(
            text('INSERT INTO resultsets (program_id, user_id, date) \
                VALUES (:program_id, :user_id, :date) \
                RETURNING id;'),
            {
                'program_id': id,
                'user_id': session['user_id'],
                'date': '2022-01-01'
            }
        )
    resultset_id = result.fetchone()[0]
    for exercise in exercise_list:
        if utils.validate_number_type(exercise) and utils.validate_number_type(exercise_list[exercise]):
            should_commit = True
            db.session.execute(
                text('INSERT INTO results (resultset, exercise_id, result) \
                    VALUES (:resultset, :exercise_id, :result);'),
                {
                    'resultset': resultset_id,
                    'exercise_id': int(exercise),
                    'result': int(exercise_list[exercise])
                }
            )
    if should_commit:
        db.session.commit()
    else:
        db.session.rollback()

def program_has_results(program_id):
    result = db.session.execute(
        text(
            """
                SELECT COUNT(id)
                FROM resultsets
                WHERE program_id = :program_id AND user_id = :user_id
            """
        ),
        {'program_id':program_id, 'user_id': session['user_id']}
    )
    return result.fetchone()[0] > 0

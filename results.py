from db import db
from flask import session
from sqlalchemy.sql import text
import utils
from datetime import date


def get_results(program_id):
    result = db.session.execute(
        text(
            """
                SELECT rs.date, e.id as eid, r.result, rs.id
                FROM exercises e
                LEFT JOIN results r on e.id = r.exercise_id
                LEFT JOIN resultsets rs on rs.id = r.resultset
                WHERE e.program_id = :program_id AND rs.user_id = :user_id
                ORDER BY rs.date DESC, rs.id
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
                'date': date.fromisoformat(exercise_list['date'])
            }
        )
    resultset_id = result.fetchone()[0]
    for exercise in exercise_list:
        if exercise != 'date' and utils.validate_number_type(exercise) and utils.validate_number_type(exercise_list[exercise]):
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

def delete_program_results(program_id):
    db.session.execute(
        text(
            """
                DELETE
                FROM results r
                WHERE r.resultset in (
                    SELECT id 
                    FROM resultsets 
                    WHERE program_id = :program_id AND user_id = :user_id
                )
            """
        ),
        {'program_id':program_id, 'user_id': session['user_id']}
    )
    db.session.execute(
        text(
            """
                DELETE
                FROM resultsets 
                WHERE program_id = :program_id AND user_id = :user_id
            """
        ),
        {'program_id':program_id, 'user_id': session['user_id']}
    )
    db.session.commit()

def resultset_exists(id):
    result = db.session.execute(
        text(
            """
                SELECT COUNT(id)
                FROM resultsets
                WHERE id = :id AND user_id = :user_id
            """
        ),
        {'id':id, 'user_id': session['user_id']}
    )
    return result.fetchone()[0] > 0

def delete_resultset(id):
    db.session.execute(
        text(
            """
                DELETE
                FROM results r
                WHERE r.resultset = :id
            """
        ),
        {'id':id, 'user_id': session['user_id']}
    )
    db.session.execute(
        text(
            """
                DELETE
                FROM resultsets 
                WHERE id = :id AND user_id = :user_id
            """
        ),
        {'id':id, 'user_id': session['user_id']}
    )
    db.session.commit()

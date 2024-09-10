from db import db
from flask import session
from sqlalchemy.sql import text


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
    for exercise in exercise_list:
        if exercise.isnumeric() and exercise_list[exercise].isnumeric():
            db.session.execute(
                    text('INSERT INTO results (resultset, exercise_id, result) \
                        VALUES (:resultset, :exercise_id, :result) \
                        RETURNING id'),
                    {
                        'resultset': resultset_id,
                        'exercise_id': int(exercise),
                        'result': int(exercise_list[exercise])
                    }
                )
            db.session.commit()

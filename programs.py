from db import db
from flask import session
from sqlalchemy.sql import text
import exercises
import results

def get_programs():
    try:
        result = db.session.execute(
            text('SELECT id, name, description FROM programs WHERE user_id = :user_id'),
            {'user_id': session['user_id']}
        )
        return result.fetchall()
    except:
        return False

def get_program(id):
    try:
        result = db.session.execute(
            text('SELECT id, name, description FROM programs WHERE id = :id AND user_id = :user_id'),
            {'id': id, 'user_id': session['user_id']}
        )
        return result.fetchone()
    except:
        return False

def create_program(name, description):
    try:
        result = db.session.execute(
                text('INSERT INTO programs (name, description, user_id) VALUES (:name, :description, :user_id) RETURNING id'),
                {'name':name, 'description':description, 'user_id': session['user_id']}
            )
        program_id = result.fetchone()[0]
        db.session.commit()
        return program_id
    except:
        return False

def update_program(id, name, description):
    try:
        db.session.execute(
            text('UPDATE programs SET name=:name, description=:description WHERE id = :id AND user_id = :user_id'),
            {'name':name, 'description':description, 'id':id, 'user_id': session['user_id']}
        )
        db.session.commit()
        return True
    except:
        return False

def delete_program(id):
    try:
        if not results.delete_program_results(id):
            return False
        if not exercises.delete_program_exercises(id):
            return False
        db.session.execute(
            text(
                """
                    DELETE
                    FROM programs 
                    WHERE id = :id AND user_id = :user_id
                """
            ),
            {'id':id, 'user_id': session['user_id']}
        )
        db.session.commit()
        return True
    except:
        return False

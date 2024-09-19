from datetime import date
from flask import session
from sqlalchemy.exc import SQLAlchemyError

def check_csrf_token(form):
    return 'csrf_token' not in form or \
        'csrf_token' not in session or \
        session['csrf_token'] != form['csrf_token']

def validate_number_type(value):
    return isinstance(value, int) or (isinstance(value, str) and value.isnumeric())

def validate(value, validation_type):
    if validation_type == 'string':
        return isinstance(value, str) and len(value) < 100
    if validation_type == 'number':
        return validate_number_type(value) and 0 <= int(value) < 1000
    if validation_type == 'date':
        try:
            return date.fromisoformat(value)
        except SQLAlchemyError:
            return False
    return False

def validate_all(strings, numbers):
    for string in strings:
        if not validate(string, 'string'):
            return False
    for number in numbers:
        if not validate(number, 'number'):
            return False
    return True

from flask import session

def check_csrf_token(form):
    return 'csrf_token' not in form or 'csrf_token' not in session or session['csrf_token'] != form['csrf_token']

def validate(value, type):
    if type == 'string':
        return type(value) == 'string' and len(value) < 1000
    if type == 'number':
        return value.isnumeric() and 0 <= int(value) < 1000
    
def validate_all(strings=[], numbers=[]):
    for string in strings:
        if (not validate(string, 'string')):
            return False
    for number in numbers:
        if (not validate(number, 'number')):
            return False
    return True
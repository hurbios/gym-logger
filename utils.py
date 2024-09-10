from flask import session

def check_csrf_token(form):
    return 'csrf_token' not in form or 'csrf_token' not in session or session["csrf_token"] != form['csrf_token']

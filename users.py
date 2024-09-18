from db import db
from flask import session
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
import secrets


def login(username, password):
    try:
        result = db.session.execute(
            text('SELECT id, pwhash FROM users WHERE username = :username'),
            {'username':username}
        )

        resultArr = result.fetchone()
        if resultArr and len(resultArr) > 0:
            user_id = resultArr[0]
            pwhash = resultArr[1]
            if check_password_hash(pwhash=pwhash, password=password):
                session['username'] = username
                session['user_id'] = user_id
                session["csrf_token"] = secrets.token_hex(16)
        return True
    except:
        return False

def logout():
    if 'username' in session:
        if 'username' in session:
            del session['username']
        if 'user_id' in session:
            del session['user_id']
        if 'csrf_token' in session:
            del session["csrf_token"]

def register(username, password):
    # Using different less secure method pbkdf2 here because macOS doesn't come with openSSL (no scrypt by default)
    hash_value = generate_password_hash(password, method='pbkdf2')
    try:
        result = db.session.execute(
            text('SELECT id, pwhash FROM users WHERE username = :username'),
            {'username':username}
        )
        resultArr = result.fetchone()
        if resultArr:
            return False
        
        sql = text('INSERT INTO users (username, pwhash) VALUES (:username, :pwhash) RETURNING id')
        db.session.execute(sql, {'username':username, 'pwhash':hash_value})
        db.session.commit()
        return login(username, password)
    except:
        return False

def regenerate_csrf():
    session["csrf_token"] = secrets.token_hex(16)

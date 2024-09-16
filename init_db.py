from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash
from db import db

def init_database():
    sql = """
        DROP TABLE IF EXISTS templates;
        DROP TABLE IF EXISTS results;
        DROP TABLE IF EXISTS resultsets;
        DROP TABLE IF EXISTS exercises;
        DROP TABLE IF EXISTS programs;
        DROP TABLE IF EXISTS users;
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username TEXT,
            pwhash TEXT
        );

        CREATE TABLE programs (
            id SERIAL PRIMARY KEY,
            name TEXT,
            description TEXT,
            user_id INTEGER REFERENCES users
        );

        CREATE TABLE exercises (
            id SERIAL PRIMARY KEY,
            name TEXT,
            sets INTEGER,
            reps INTEGER,
            program_id INTEGER REFERENCES programs,
            user_id INTEGER REFERENCES users
        );

        CREATE TABLE resultsets (
            id SERIAL PRIMARY KEY,
            program_id INTEGER REFERENCES programs,
            user_id INTEGER REFERENCES users,
            date DATE
        );

        CREATE TABLE results (
            id SERIAL PRIMARY KEY,
            exercise_id INTEGER REFERENCES exercises,
            resultset INTEGER REFERENCES resultsets,
            result INTEGER
        );

        CREATE TABLE templates (
            id SERIAL PRIMARY KEY,
            name TEXT,
            user_id INTEGER REFERENCES users
        );
    """
    db.session.execute(text(sql))
    db.session.commit()

def add_test_data():
    hash1 = generate_password_hash('test', method="pbkdf2")
    hash2 = generate_password_hash('asdf', method="pbkdf2")
    sql = """
        INSERT INTO users (id, username, pwhash) VALUES (1, 'testuser', :hash1);
        INSERT INTO users (id, username, pwhash) VALUES (2, 'asdfasdf', :hash2);
        
        INSERT INTO programs (id, name, description, user_id) VALUES (1, 'Full body', 'Just a full body workout...', 1);
        INSERT INTO exercises (id, name, sets, reps, program_id, user_id) VALUES (1, 'bench press', 3, 10, 1, 1);
        INSERT INTO exercises (id, name, sets, reps, program_id, user_id) VALUES (2, 'back squat', 3, 10, 1, 1);
        INSERT INTO exercises (id, name, sets, reps, program_id, user_id) VALUES (3, 'weighted pull up', 3, 10, 1, 1);
        INSERT INTO exercises (id, name, sets, reps, program_id, user_id) VALUES (4, 'push press', 4, 10, 1, 1);
        INSERT INTO exercises (id, name, sets, reps, program_id, user_id) VALUES (5, 'barbell curl', 3, 10, 1, 1);
        INSERT INTO exercises (id, name, sets, reps, program_id, user_id) VALUES (6, 'sit ups', 3, 10, 1, 1);
        
        INSERT INTO programs (id, name, description, user_id) VALUES (2, 'Penakone', 'Perus penkkihaukkareeni', 1);
        INSERT INTO exercises (id, name, sets, reps, program_id, user_id) VALUES (7, 'vinopena', 4, 10, 2, 1);
        INSERT INTO exercises (id, name, sets, reps, program_id, user_id) VALUES (8, 'ojentajat', 3, 10, 2, 1);
        INSERT INTO exercises (id, name, sets, reps, program_id, user_id) VALUES (9, 'haukka', 2, 12, 2, 1);
        INSERT INTO exercises (id, name, sets, reps, program_id, user_id) VALUES (10, 'ylätalja', 3, 12, 2, 1);
        
        INSERT INTO programs (id, name, description, user_id) VALUES (3, 'pure legs', 'Make your legs buuuurrrrnnnn!', 2);
        INSERT INTO exercises (id, name, sets, reps, program_id, user_id) VALUES (11, 'Front squat', 5, 5, 3, 2);
        INSERT INTO exercises (id, name, sets, reps, program_id, user_id) VALUES (12, 'Deadlift', 5, 5, 3, 2);
        INSERT INTO exercises (id, name, sets, reps, program_id, user_id) VALUES (13, 'Leg press', 3, 12, 3, 2);
        INSERT INTO exercises (id, name, sets, reps, program_id, user_id) VALUES (14, 'Leg curl', 3, 12, 3, 2);
        INSERT INTO exercises (id, name, sets, reps, program_id, user_id) VALUES (15, 'Standing calves', 3, 12, 3, 2);

        INSERT INTO programs (id, name, description, user_id) VALUES (4, 'Fat to fit in 2 days', 'Program to lose weight 20kg and gain muscle 15kg in 2 days!!1', 2);
        INSERT INTO exercises (id, name, sets, reps, program_id, user_id) VALUES (16, 'snatch', 3, 5, 4, 2);
        INSERT INTO exercises (id, name, sets, reps, program_id, user_id) VALUES (17, 'gobblet squat', 3, 20, 4, 2);
        INSERT INTO exercises (id, name, sets, reps, program_id, user_id) VALUES (18, 'land mines', 3, 20, 4, 2);
        INSERT INTO exercises (id, name, sets, reps, program_id, user_id) VALUES (19, 'barbell curl', 3, 20, 4, 2);

        INSERT INTO templates (id, name) VALUES (1, 'barbell curl');
        INSERT INTO templates (id, name) VALUES (2, 'bench press');
        INSERT INTO templates (id, name) VALUES (3, 'back squat');
        INSERT INTO templates (id, name) VALUES (4, 'front squat');
        INSERT INTO templates (id, name) VALUES (5, 'deadlift');
        INSERT INTO templates (id, name) VALUES (6, 'sumo deadlift');
        INSERT INTO templates (id, name) VALUES (7, 'push press');
        INSERT INTO templates (id, name) VALUES (8, 'bicep curl');
        INSERT INTO templates (id, name) VALUES (9, 'leg press');
        INSERT INTO templates (id, name) VALUES (10, 'leg curl');
        INSERT INTO templates (id, name) VALUES (11, 'pull up');
        INSERT INTO templates (id, name) VALUES (12, 'chin up');
    """
    db.session.execute(text(sql), { "hash1":hash1, "hash2":hash2 })
    db.session.commit()
    
    # fix serialized keys broken in mass insert. (https://stackoverflow.com/questions/18232714/postgresql-next-serial-value-in-a-table)
    db.session.execute(text("SELECT setval(pg_get_serial_sequence('users','id'), 2)"))
    db.session.commit()
    db.session.execute(text("SELECT setval(pg_get_serial_sequence('programs','id'), 4)"))
    db.session.commit()
    db.session.execute(text("SELECT setval(pg_get_serial_sequence('exercises','id'), 19)"))
    db.session.commit()
    db.session.execute(text("SELECT setval(pg_get_serial_sequence('templates','id'), 12)"))
    db.session.commit()

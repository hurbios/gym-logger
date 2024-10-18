DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS resultsets;
DROP TABLE IF EXISTS exercises;
DROP TABLE IF EXISTS programs;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE,
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

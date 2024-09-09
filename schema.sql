CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username TEXT,
  pwhash TEXT
);

CREATE TABLE programs (
  id SERIAL PRIMARY KEY,
  name TEXT,
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

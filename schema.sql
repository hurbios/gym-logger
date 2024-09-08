
CREATE TABLE programs (
  id SERIAL PRIMARY KEY,
  name TEXT,
  user INTEGER
);

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username TEXT,password TEXT
);

CREATE TABLE exercises (
  id SERIAL PRIMARY KEY,
  name TEXT,
  sets INTEGER,
  reps INTEGER,
  program_id INTEGER REFERENCES programs,
  user_id INTEGER REFERENCES users
);

CREATE TABLE programs (
  id SERIAL PRIMARY KEY,
  name TEXT,
  user INTEGER
);

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username TEXT,password TEXT
);
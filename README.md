# gym-logger
The Gym Logger app is a web application for logging gym workouts. 

The application allows:
  - creating new programs
  - creating workouts for the programs
  - adding exercises for the workouts 
  - loggin the results of the exercises for each workout set

There can be multiple users and each of the users have their own workouts, programs etc. The users must to login to see their data, manage their programs and results. The results can be edited and new ones can be added.

The program allows only adding exercise results of the results that are in the selected program. The application allows only creating full body workouts in the first version so a program can have only one type of workout.

## Quick start guide
### Prerequisites
- postgresql installed, db created for the application and running
- python3 (& pip) installed

### Quick start guide for local testing 
(more detailed instructions in later sections if needed)

Replace `<< YOUR_DATABASE_NAME >>` in following steps with db name that you wish to use with this application, e.g. `test`.
Replace `<< YOUR_SECRET_FOR_SESSIONS >>` with some random length string containing a-z,0-9 chars, e.g. `asdf34tfg43gsag43ag4b3boaeibb3b3`

- Create `.env` file in the root directory of this app containing the following properties:
  - ```
    DATABASE_URL=postgresql:///<< YOUR_DATABASE_NAME >>
    SECRET_KEY=<< YOUR_SECRET_FOR_SESSIONS >>
    FLASK_ENV=develop

Run following commands in the root directory of this app:
- `psql -d << YOUR_DATABASE_NAME >> < schema.sql`
- `python3 -m venv venv`
- `source venv/bin/activate`
- `python -m pip install --upgrade pip`
- `pip install -r requirements.txt`
- `flask --app app.py --debug run`

Open browser and navigate to http://localhost:5000/

Additionally, some test data can be created by navigating to `http://localhost:5000/init_db`.
- This will replace existing data in the tables this application is using
- 2 test users will be created (username:password):
  - testuser:test
  - asdfasdf:asdf

The application can be quit with `ctrl + c` and the virtual environment can be exited with `deactivate` after testing.


## More detailed intructions
### Create virtual python env
- Create the virtual environment by running `python3 -m venv venv`
- Run `source venv/bin/activate` to activate the environment

### Install dependencies
- `python -m pip install --upgrade pip`
- `pip install -r requirements.txt`
  - if python requirements installation fails the components can be installed separately:
    - `pip install flask`
    - `pip install flask-sqlalchemy`
    - `pip install psycopg2`
    - `pip install python-dotenv`


#### Troubleshooting
If `psycopg2` doesn't install properly try installing `psycopg2-binary`

### Running locally (localhost)
- Create `.env` file containing the following properties:
  - ```
    DATABASE_URL=postgresql:///<< YOUR_DATABASE_NAME >>
    SECRET_KEY=<< YOUR_SECRET_FOR_SESSIONS >>
    FLASK_ENV=develop
  - FLASK_ENV is used in this app for enabling `/init_db` endpoint only in develop env.
  
- `psql -d << YOUR_DATABASE_NAME >> < schema.sql` for initializing db before using.
  - (e.g. `psql -d test < schema.sql`)
  - Other option is to use `/init_db` endpoint for initializing db with test data after starting flask. NOTE: This requires the app to be running. 
- Run production version with `flask run` with FLASK_ENV=production environment variable or run development version with `flask --app app.py --debug run` with FLASK_ENV=develop environment variable

The application can be quit with `ctrl + c` and the virtual environment can be exited with `deactivate` after testing.

#### Test data
- Test data created with `/init_db` will replace existing data and tables with the table names in schema in the db. The init_db endpoint initializes with data meant only for test purposes and is not mandatory for making the app work. The test data contains 2 users with following credentials:
  - testuser:test
  - asdfasdf:asdf

## links
- Icons from google fonts: https://fonts.google.com/
- Styles from bootstrap: https://getbootstrap.com

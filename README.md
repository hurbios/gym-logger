# gym-logger
The Gym Logger app is a web application for logging gym workouts. 

The application allows:
  - creating new programs
  - creating workouts for the programs
  - adding exercises for the workouts 
  - loggin the results of the exercises for each workout set

There can be multiple users and each of the users have their own workouts, programs etc. The users must to login to see their data, manage their programs and results. The results can be edited and new ones can be added.

The program allows only adding exercise results of the results that are in the selected program. The application allows only creating full body workouts in the first version so a program can have only one type of workout.

## How to run locally
### Prerequisites
- postgresql installed, db created for the application and running
- python3 (& pip) installed

### Install dependencies
- `python3 -m venv venv`
- `source venv/bin/activate`
- `python3 -m pip install --upgrade pip`
- `pip install flask`
- `pip install flask-sqlalchemy`
- `pip install psycopg2` // if doesn't install properly try installing psycopg2-binary
- `pip install python-dotenv`

### Running locally (localhost)
- Create `.env` file containing the following properties:
  - ```
    DATABASE_URL=postgresql:///<< YOUR_DATABASE_NAME >>
    SECRET_KEY=<< YOUR_SECRET_FOR_SESSIONS >>
    FLASK_ENV=develop
  - FLASK_ENV is used only for `/init_db` endpoint
  
- `psql < schema.sql` for initializing db before using.
  - Other option is to use `/init_db` endpoint for initializing db with test data after starting flask. NOTE: This requires the app to be running. 
- Run production version wiht `flask run` or run development version with `flask --app app.py --debug run`

#### Test data
- Test data created with `/init_db` will replace existing data and tables with the table names in schema in the db. The init_db endpoint initializes with data meant only for test purposes and is not mandatory for making the app work. The test data contains 2 users with following credentials:
  - testuser:test
  - asdfasdf:asdf

## links
- Icons from google fonts: https://fonts.google.com/
- Styles from bootstrap: https://getbootstrap.com

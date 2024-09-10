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
Run production version wiht `flask run` or run development version with `flask --app app.py --debug run`

`python3 -m venv venv`
`source venv/bin/activate`
`python3 -m pip install --upgrade pip`
`pip install flask`
`pip install flask-sqlalchemy`
`pip install psycopg2` // if doesn't install properly install psycopg2-binary
`pip install python-dotenv`


/Applications/Postgres.app/Contents/Versions/latest/bin/psql


## TODO
- DB connection -- Done
- authentication -- Done
- user creation -- Done
- Program creation -- Done
- Reformat endpoints -- Done
- Workout program creation
  - exercise additions -- Done
  - exercise deletions -- Done
  - exercise edit -- Done
- DB init - Done
- test data creation - Done
- add pylint - Done
- Workout program name edition - Done
- Add selectable exercise templates - Done
- Add possiblity to add results - Done
- Refactor to separate modules - Done
- Disable workout program edition if results entered - TODO
- Input validations
  - frontend - TODO
  - backend - TODO
- Workout program Deletion - TODO
- Dev setup - TODO
- add CSRF protection -TODO
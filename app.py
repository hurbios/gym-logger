from flask import Flask
from flask import redirect, render_template, request, session
from os import getenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
app.secret_key = getenv("SECRET_KEY")

#### Landing page ####
@app.route("/")
def index():
  programs = []
  if("username" in session):
    result = db.session.execute(text('SELECT id, name FROM programs WHERE userId = :user'), {"user": session["user_id"]})
    programs = result.fetchall() 
  return render_template("index.html", programs = programs)

#### AUTH ####
@app.route("/login", methods=["POST"])
def login():
  username = request.form["username"]
  password = request.form["password"]

  result = db.session.execute(text('SELECT id,password FROM users WHERE username = :username'), {"username":username})
  resultArr = result.fetchone()
  if(resultArr and len(resultArr)>0):
    user_id = resultArr[0]
    pwhash = resultArr[1]
    if (check_password_hash(pwhash=pwhash, password=password)):
      session["username"] = username
      session["user_id"] = user_id
  return redirect("/")

@app.route("/logout")
def logout():
  if("username" in session):
    del session["username"]
  return redirect("/")


#### USER CREATION ####
@app.route("/create-user")
def create_user():
  if("username" in session):
      return redirect("/")
  return render_template("create-user.html")

@app.route("/api/create-user", methods=["POST"])
def create_user_api():
  if("username" in session):
      return redirect("/")
  username = request.form["username"]
  password = request.form["password"]
  hash_value = generate_password_hash(password, method="pbkdf2") # Using different less secure method here because macOS doesn't come with openSSL
  sql = text("INSERT INTO users (username, password) VALUES (:username, :password) RETURNING id")
  user_id= db.session.execute(sql, {"username":username, "password":hash_value})
  db.session.commit()
  session["username"] = username
  session["user_id"] = user_id
  return redirect("/")


#### PROGRAM ENDPOINTS ####
@app.route("/create-program")
def create_program():
  if("username" not in session):
    return redirect("/")
  print(session)
  return render_template("create-new-program.html")

@app.route("/api/create-program", methods=["POST"])
def create_program_api():
  if("username" not in session):
    return redirect("/")
  name = request.form['programName']
  result = db.session.execute(text('INSERT INTO programs (name, userId) VALUES (:name, :user) RETURNING id'), {"name":name, "user": session["user_id"]})
  poll_id = result.fetchone()[0]
  db.session.commit()
  return redirect("/edit-program/"+str(poll_id))

@app.route("/edit-program/<int:id>")
def edit_program(id):
  if("username" not in session):
    return redirect("/")
  result = db.session.execute(text('SELECT id, name FROM programs WHERE id = :id AND userId = :user'), {"id":id, "user": session["user_id"]})
  program = result.fetchone()
  result = db.session.execute(text('SELECT id, name, sets, reps FROM exercises WHERE program_id = :id AND user_id = :user'), {"id":id, "user": session["user_id"]})
  exercises = result.fetchall()
  if(not program or len(program) < 1):
    return redirect("/")
  return render_template("edit-program.html", program_name = program[1], program_id = id, exercises=exercises)

@app.route("/add-exercise", methods=["POST"])
def add_exercise():
  if("username" not in session):
    return redirect("/")
  name = request.form["exercise_name"]
  sets = request.form["exercise_sets"]
  reps = request.form["exercise_reps"]
  program_id = request.form["program_id"] # TODO: validate that program belongs to the user
  sql = text("INSERT INTO exercises (name, reps, sets, program_id, user_id) VALUES (:name, :reps, :sets, :program_id, :user_id) RETURNING id")
  exercise_id= db.session.execute(sql, { "name": name, "sets": sets, "reps": reps, "program_id": program_id, "user_id": session["user_id"] })
  db.session.commit()
  return redirect("/edit-program/" + str(program_id))

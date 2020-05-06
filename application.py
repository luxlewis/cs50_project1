import os
from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from argon2 import PasswordHasher


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register")
def get_register_form():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    ph = PasswordHasher()
    hash = ph.hash(password)

    email_already_exists = db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).rowcount > 0
    if email_already_exists:
        return render_template("register.html")

    username_already_exists = db.execute("SELECT * FROM users WHERE username = :username",
                                         {"username": username}).rowcount > 0
    if username_already_exists:
        return render_template("register.html")


    db.execute("INSERT INTO users (first_name, last_name, email, username, password) VALUES (:first_name, :last_name, :email, :username, :password)",
        {"first_name": first_name, "last_name": last_name, "email": email, "username": username, "password": hash})

    db.commit()


    return render_template("book_search.html")


@app.route("/login")
def get_login_form():
    return render_template("login.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == 'POST' and "username" in request.form and "password" in request.form:
        username = request.form.get("username")
        password = request.form.get("password")
        user = db.execute("SELECT * FROM users WHERE username = :username AND password = :password",
               {"username": username, "password": password}).fetchone()
    # If account exists in users table in database
        if user:
            # Create session data
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']

            db.commit()

            return redirect(url_for("book_search"))
        else:
            return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return render_template("logout.html")

@app.route("/book_search")
def book_search():
    # Check if user is loggedin
    if 'loggedin' in session:
        return render_template("book_search.html", username=session['username'])
    # User is not loggedin redirect to login page
    else:
        return redirect(url_for("login"))


if __name__ == "__main__":
    app.run()

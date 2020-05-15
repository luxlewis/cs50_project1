import os
import csv
import requests
from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from argon2 import PasswordHasher
import io
import urllib
from PIL import Image


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
        return render_template("register.html", message="email already exists!")

    username_already_exists = db.execute("SELECT * FROM users WHERE username = :username",
                                         {"username": username}).rowcount > 0
    if username_already_exists:
        return render_template("register.html", message="username already exists!")


    db.execute("INSERT INTO users (first_name, last_name, email, username, password) VALUES (:first_name, :last_name, :email, :username, :password)",
        {"first_name": first_name, "last_name": last_name, "email": email, "username": username, "password": password})

    db.commit()

    return render_template("login.html", )


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
            return render_template("login.html", message="Sorry, check username/password is correct and try again.\n")

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


@app.route("/book_search", methods=["POST"])
def get_search_results():
    author = request.form.get("author")
    title = request.form.get("title")
    isbn = request.form.get("isbn")
    query = author + title + isbn
    search_text = "%" + query + "%"
    results = db.execute("SELECT * FROM books WHERE author ILIKE :query OR title ILIKE :query OR isbn LIKE :query",
                         {"query": search_text}).fetchall()
    if results:
        return render_template("search_results.html", results=results)

    else:
        return render_template("book_search.html")


@app.route("/api/<isbn>")
def book_api(isbn):
    results = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if results is None:
        return render_template("book_search.htm")
    return jsonify({
        "Title": results.title,
        "Author": results.author,
        "year": results.year,
        "ISBN": results.isbn,
    })
db.commit()

@app.route("/book_search/<isbn>")
def book_page(isbn):
    results = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if results is None:
        return render_template("search_results.html")
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": "OxVIu40NJp0S4DBt18tGtA", "isbns": isbn})
    data = res.json()
    # pprint(data)
    book_option = data['books']
    average_rating = book_option[0]['average_rating']
    ratings_count = book_option[0]['ratings_count']
    return render_template("book_page.html", results=results, average_rating=average_rating,
                           ratings_count=ratings_count, isbn=isbn)


db.commit()


# @app.route("/book_search/review", methods=['GET','POST'])
# def leave_review():
#     return render_template("review.html")
#
# @app.route("/book_search/review", methods=['GET', 'POST'])
# def submit_review():
#     if request.method == 'POST':
#         book_rating = request.form.get("book_rating")
#         book_rating_text = request.form.get("book_review_data")
#         db.execute("INSERT INTO book_reviews (book_rating, book_rating_text, isbn) VALUES (:book_rating :book_rating_text, :isbn)",
#                    {"book_rating": book_rating, "book_rating_text": book_rating_text, "isbn": isbn})
#
#         return render_template("book_page.html", book_rating=book_rating, book_rating_text=book_rating_text, isbn=isbn, results=results, ratings_count=ratings_count, average_rating=average_rating)
#

if __name__ == "__main__":
    app.run()
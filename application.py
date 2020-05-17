import os
import csv
import requests
from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker



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
            return render_template("login.html", message="Incorrect username or password please try again.\n")

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
        return render_template("error.html", message="Hmm, no matches...please search again.")



@app.route("/api/<isbn>")
def book_api(isbn):
    results = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if results is None:
        return render_template("error.html", message="404 Error Not Found")
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
    reviews = db.execute("SELECT book_rating, book_rating_text, username FROM user_reviews WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
    print(reviews)
    if results is None:
        return render_template("search_results.html")
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": "OxVIu40NJp0S4DBt18tGtA", "isbns": isbn})
    data = res.json()
    # pprint(data)
    book_option = data['books']
    average_rating = book_option[0]['average_rating']
    ratings_count = book_option[0]['ratings_count']
    return render_template("book_page.html",  reviews=reviews, results=results, average_rating=average_rating,
                           ratings_count=ratings_count, isbn=isbn)


db.commit()


@app.route("/book_search/<isbn>", methods=['POST'])
def submit_review(isbn):
    username = session.get("username")
    too_many_reviews = db.execute("SELECT * FROM user_reviews WHERE isbn = :isbn AND username = :username",
                                  {"isbn": isbn, "username": username}).fetchone()
    if request.method == 'POST' and too_many_reviews is None:
        book_rating = request.form.get("book_rating")
        username = session.get("username")
        book_rating_text = request.form.get("book_rating_text")

        book_id = db.execute("SELECT id from books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()[0]

        db.execute("INSERT INTO user_reviews (isbn, book_rating, book_rating_text, book_id, username) VALUES (:isbn, :book_rating, :book_rating_text, :book_id, :username)",
                   {"book_rating": book_rating, "book_rating_text": book_rating_text, "isbn": isbn, "book_id": book_id, "username": username})
        reviews = db.execute("SELECT * FROM user_reviews WHERE isbn = :isbn", {"isbn": isbn}).fetchall()

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
    else:
        return render_template("error.html", message="you've already reviewed that book")
    db.commit()
    return render_template("book_page.html", book_rating=book_rating, book_rating_text=book_rating_text, isbn=isbn, ratings_count=ratings_count, results=results, average_rating=average_rating, reviews=reviews)


if __name__ == "__main__":
    app.run()
import requests
import os
import csv
from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from pprint import pprint

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "OxVIu40NJp0S4DBt18tGtA", "isbns": isbn_url})
data = res.json()
# pprint(data)
book_option = data['books']
average_rating = book_option[0]['average_rating']
ratings_count = book_option[0]['ratings_count']
isbn = int(book_option[0]['isbn'])
db.execute("INSERT INTO book_review_data (isbn, average_rating, ratings_count) VALUES (:isbn, :average_rating, :ratings_count)", {"isbn": isbn, "average_rating": average_rating, "ratings_count": ratings_count})

db.commit()
pprint(isbn)
pprint(average_rating)
pprint(ratings_count)



#
# f = open("books.csv")
# reader = csv.reader(f)
# for isbn in reader:
#   db.execute("INSERT INTO book_review_data (isbn) VALUES (:isbn)", {"isbn": isbn})
# db.commit()


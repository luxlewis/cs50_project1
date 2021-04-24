# Project 1

### [cs50 Web Programming with Python and JavaScript](https://cs50.harvard.edu/web/2020/) ###

**Demo**

[Biblio-files](https://www.youtube.com/watch?v=kiBB9qgR15A&ab_channel=AlexandraLewis)

My project is called Biblio-files. It is a book review website. Users can register for the website and then log in using their username and password. Once they log in, they will be able to search for books, leave reviews for individual books, and see the reviews made by other people. I use a third-party API by Goodreads, to pull in ratings from a broader audience. Finally, users can query for book details and book reviews programmatically via the website’s API.

It contains the following:

**Application.py** - this is the main program which includes all of the code which runs flask. I have 8 flask app routes including register/login/logout/book_search/API request/search_results/book_page/submit_review.

**import.py** - This file imports the books.csv file into a postgres database called books.

**tables.sql** - creates the database tables necessary to run the program.

**Templates** - there are 10 templates, including a base.html/error.html/index.html/register.html/book_search.html/search_results.html/book_page.html/login/logout.html/api.html.

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    username VARCHAR NOT NULL,
    password VARCHAR NOT NULL
);

CREATE TABLE user_reviews (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR,
    book_rating INTEGER NOT NULL,
    book_rating_text VARCHAR NOT NULL,
    book_id INTEGER REFERENCES books,
    username VARCHAR NOT NULL
);

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year INTEGER NOT NULL
);
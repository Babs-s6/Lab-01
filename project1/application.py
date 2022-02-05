import os
import requests
import json
from flask import Flask, session, request, render_template, redirect, url_for, flash, jsonify, abort

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

@app.route("/login", methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    result = db.execute(f"SELECT * from users WHERE password='{password}';")
    if result.rowcount == 1:
        session['username'] = username
        flash("Logged in successfully.")
        return redirect(url_for('search'))
    flash("Error: username and password doesn't match")
    return render_template("index.html")


@app.route("/register_form", methods=['GET'])
def register_form():
    return render_template("register.html")

@app.route("/register", methods=['POST'])
def register():
    username = request.form.get('uname').lower()
    password = request.form.get('password')
    result = db.execute(f"SELECT * from users where username='{username}'")
    if result.rowcount == 1:
        flash("Error: The entered username is taken. please try a different username.")
        return redirect(url_for('register_form'))

    db.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')")
    db.commit()
    session['username'] = username
    flash("You are now registered and logged in successfully. You can now search the books in the blow form.")
    return redirect(url_for('search'))



@app.route("/logout", methods=['GET'])
def logout():
    del session['username']
    flash("Logged out successfully.")
    return redirect(url_for('index'))


@app.route("/search", methods=['GET'])
def search():
    if 'username' not in session:
        flash("You are not logged in!")
        return redirect(url_for('index'))
    isbn = request.args.get('isbn')
    title = request.args.get('title')
    author = request.args.get('author')
    # print(isbn, title, author)
    if not (isbn or title or author):
        return render_template("search.html")

    results = db.execute(
        f"select * from books where isbn ILIKE '%{isbn}%' and title ILIKE '%{title}%' and author ILIKE '%{author}%'"
    )
    result_list = []
    for r in results:
        result_list.append({'isbn': r[0], 'title': r[1], 'author': r[2], 'year': r[3]})
    return render_template('search.html', search_result=result_list, isbn=isbn, title=title, author=author)


@app.route("/book/<isbn>", methods=['GET'])
def book_page(isbn):
    if 'username' not in session:
        flash("You are not logged in!")
        return redirect(url_for('index'))

    results = db.execute(f"SELECT * FROM books WHERE isbn = '{isbn}'")
    if results.rowcount == 0:
        return "Book Not found!"
    book = results.first()

    reviews = db.execute(f"SELECT * FROM book_reviews WHERE book_isbn='{isbn}'")
    reviews_list = []
    for review in reviews:
        reviews_list.append({'username': review[1], 'review': review[2], 'rating': review[3]})

    google_api="https://www.googleapis.com/books/v1/volumes"
    res=requests.get("https://www.googleapis.com/books/v1/volumes", params={"q": f"isbn:{isbn}"}).json()
    try:
        average_rating = res['items'][0]['volumeInfo']['averageRating']
        rating_count = res['items'][0]['volumeInfo']['ratingsCount']
    except KeyError:
        average_rating = "Not available"
        rating_count = "Not available"

    return render_template(
        "book_page.html",
        isbn=book[0], title=book[1], author=book[2], year=book[3],
        search_result=reviews_list,
        average_rating=average_rating,
        rating_count=rating_count,
    )


@app.route("/submit-review", methods=['POST'])
def submit_review():
    if 'username' not in session:
        flash("You are not logged in!")
        return redirect(url_for('index'))
    username = session['username']
    isbn = request.form.get('isbn')

    result = db.execute(
        f"SELECT * FROM book_reviews WHERE reviewer_username='{username}' AND book_isbn='{isbn}'"
    )
    if result.rowcount == 1:
        flash("Error: Sorry, you've previously wrote a review for this book.")
        return render_template("book_page.html", isbn=isbn)

    review = request.form.get('review')
    rating = request.form.get('score')

    db.execute(
        f"INSERT INTO book_reviews (book_isbn, reviewer_username, review, rating) VALUES ('{isbn}', '{username}', '{review}', '{rating}')"
    )
    db.commit()
    flash("Your review successfully published.")
    return render_template("book_page.html", isbn=isbn)


@app.route("/api/<isbn>", methods=['GET', 'POST'])
def api(isbn):
    if 'username' not in session:
        flash("You are not logged in!")
        return redirect(url_for('index'))

    results = db.execute(f"SELECT * FROM books WHERE isbn = '{isbn}'")
    if results.rowcount == 0:
        abort(404)

    google_api="https://www.googleapis.com/books/v1/volumes"
    res=requests.get(google_api, params={'q': f'isbn={isbn}'}).json()
    if res['totalItems'] == 0:
        abort(404)
    average_rating = res['items'][0]['volumeInfo'].get('averageRating')
    rating_count = res['items'][0]['volumeInfo'].get('ratingsCount')
    published_date = res['items'][0]['volumeInfo'].get('publishedDate')
    identifiers = res['items'][0]['volumeInfo'].get('industryIdentifiers')
    ISBN_10 = None
    ISBN_13 = None
    for identifier in identifiers:
        if identifier.get('type') == 'ISBN_10':
            ISBN_10 = identifier.get('identifier')
        if identifier.get('type') == 'ISBN_13':
            ISBN_13 = identifier.get('identifier')

    book = results.first()
    book_res = {
        'title': book[1],
        'author': book[2],
        'publishedDate': published_date,
        "ISBN_10": ISBN_10,
        "ISBN_13": ISBN_13,
        "reviewCount": rating_count,
        "averageRating": average_rating,
    }
    return jsonify(book_res)

app.run()

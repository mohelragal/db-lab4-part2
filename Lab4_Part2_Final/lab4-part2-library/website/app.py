"""Lab 4 Part II: simple Flask + MySQL library website (no ORM)."""

import os
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pymysql
from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for

load_dotenv(Path(__file__).with_name('.env'))

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'local-development-change-me')


def db():
    """Open a new MySQL connection. Closed by each helper below."""
    return pymysql.connect(
        host=os.getenv('DB_HOST', '127.0.0.1'),
        port=int(os.getenv('DB_PORT', '3306')),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database='library',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


def rows(sql, params=()):
    connection = db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        connection.close()


def one(sql, params=()):
    connection = db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()
    finally:
        connection.close()


def change(sql, params=()):
    connection = db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            count = cursor.rowcount
        connection.commit()
        return count
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


@app.template_filter('money')
def money(value):
    return '-' if value is None else f'{value:,.2f}'


@app.route('/')
def home():
    return redirect(url_for('search_books'))


# F2.1 - Search books using placeholder parameters, never SQL string concatenation.
@app.route('/search')
def search_books():
    categories = rows('SELECT category_id, name FROM CATEGORY ORDER BY name')
    keyword = request.args.get('keyword', '').strip()
    minimum = request.args.get('min_price', '').strip()
    maximum = request.args.get('max_price', '').strip()
    category = request.args.get('category_id', '').strip()
    error = None
    try:
        min_price = Decimal(minimum) if minimum else Decimal('0')
        max_price = Decimal(maximum) if maximum else Decimal('99999999.99')
        if not min_price.is_finite() or not max_price.is_finite():
            raise ValueError()
        if min_price < 0 or max_price < min_price or max_price > Decimal('99999999.99'):
            raise ValueError()
        category_id = int(category) if category else None
        if category_id is not None and category_id not in {c['category_id'] for c in categories}:
            raise ValueError()
    except (InvalidOperation, ValueError):
        error = 'Enter valid prices (minimum must not exceed maximum) and a valid category.'
        books = []
    else:
        books = rows('''
            SELECT b.book_id, b.title, b.price, c.name AS category
            FROM BOOK AS b
            JOIN CATEGORY AS c ON b.category_id = c.category_id
            WHERE b.title LIKE %s AND b.price BETWEEN %s AND %s
              AND (%s IS NULL OR b.category_id = %s)
            ORDER BY b.price ASC, b.title ASC
        ''', ('%' + keyword + '%', min_price, max_price, category_id, category_id))
    return render_template('search.html', books=books, categories=categories,
                           keyword=keyword, minimum=minimum, maximum=maximum,
                           category=category, error=error)


# F2.2 - Catalogue with 3 joins.
@app.route('/catalogue')
def catalogue():
    books = rows('''
        SELECT b.book_id, b.title, b.price, b.publish_year,
               a.name AS author, p.name AS publisher, c.name AS category
        FROM BOOK AS b
        JOIN AUTHOR AS a ON b.author_id = a.author_id
        JOIN PUBLISHER AS p ON b.publisher_id = p.publisher_id
        JOIN CATEGORY AS c ON b.category_id = c.category_id
        ORDER BY b.title
    ''')
    return render_template('catalogue.html', books=books)


# F2.3 - GROUP BY and HAVING reports.
@app.route('/reports')
def reports():
    categories = rows('''
        SELECT c.name AS category, COUNT(b.book_id) AS book_count,
               AVG(b.price) AS average_price
        FROM CATEGORY AS c
        LEFT JOIN BOOK AS b ON c.category_id = b.category_id
        GROUP BY c.category_id, c.name ORDER BY c.name
    ''')
    authors = rows('''
        SELECT a.name AS author, COUNT(b.book_id) AS book_count
        FROM AUTHOR AS a JOIN BOOK AS b ON a.author_id = b.author_id
        GROUP BY a.author_id, a.name HAVING COUNT(b.book_id) >= 2
        ORDER BY book_count DESC, a.name
    ''')
    totals = one('''
        SELECT SUM(price) AS total_price, MIN(price) AS minimum_price,
               MAX(price) AS maximum_price FROM BOOK
    ''')
    return render_template('reports.html', categories=categories, authors=authors, totals=totals)


# F2.4 - Active loans and LEFT JOIN lists.
@app.route('/loans')
def loans():
    active = rows('''
        SELECT l.loan_id, b.title AS book, m.name AS member,
               l.loan_date, l.return_date
        FROM LOAN AS l JOIN BOOK AS b ON l.book_id = b.book_id
        JOIN `MEMBER` AS m ON l.member_id = m.member_id
        WHERE l.return_date IS NULL ORDER BY l.loan_date
    ''')
    no_loans = rows('''
        SELECT m.member_id, m.name, m.email
        FROM `MEMBER` AS m LEFT JOIN LOAN AS l ON m.member_id = l.member_id
        WHERE l.loan_id IS NULL ORDER BY m.name
    ''')
    never_borrowed = rows('''
        SELECT b.book_id, b.title
        FROM BOOK AS b LEFT JOIN LOAN AS l ON b.book_id = l.book_id
        WHERE l.loan_id IS NULL ORDER BY b.title
    ''')
    return render_template('loans.html', active=active, no_loans=no_loans,
                           never_borrowed=never_borrowed)


# F2.5 - Top 3 books and #1 member.
@app.route('/most-borrowed')
def most_borrowed():
    books = rows('''
        SELECT b.book_id, b.title, COUNT(l.loan_id) AS loan_count
        FROM BOOK AS b LEFT JOIN LOAN AS l ON b.book_id = l.book_id
        GROUP BY b.book_id, b.title ORDER BY loan_count DESC, b.title LIMIT 3
    ''')
    member = one('''
        SELECT m.member_id, m.name, COUNT(l.loan_id) AS loan_count
        FROM `MEMBER` AS m LEFT JOIN LOAN AS l ON m.member_id = l.member_id
        GROUP BY m.member_id, m.name ORDER BY loan_count DESC, m.name LIMIT 1
    ''')
    return render_template('most_borrowed.html', books=books, member=member)


# F2.6 - Author counts including zero; matching country of publisher.
@app.route('/authors-and-books')
def authors_and_books():
    authors = rows('''
        SELECT a.author_id, a.name, COUNT(b.book_id) AS book_count
        FROM AUTHOR AS a LEFT JOIN BOOK AS b ON a.author_id = b.author_id
        GROUP BY a.author_id, a.name ORDER BY a.name
    ''')
    same_country = rows('''
        SELECT b.title, a.name AS author, p.name AS publisher, a.country
        FROM BOOK AS b JOIN AUTHOR AS a ON b.author_id = a.author_id
        JOIN PUBLISHER AS p ON b.publisher_id = p.publisher_id
        WHERE a.country = p.country ORDER BY b.title
    ''')
    return render_template('authors_and_books.html', authors=authors, same_country=same_country)


# Small, optional Lab 3 compatibility pages: list/add/edit/delete books and authors.
# The 6 new Lab 4 pages above are independent of these older CRUD actions.
@app.route('/library')
def library():
    books = rows('''
        SELECT b.book_id, b.title, b.price, a.name AS author
        FROM BOOK AS b JOIN AUTHOR AS a ON b.author_id = a.author_id
        ORDER BY b.book_id
    ''')
    authors = rows('SELECT author_id, name, country FROM AUTHOR ORDER BY author_id')
    return render_template('library.html', books=books, authors=authors)


def book_lists():
    return (rows('SELECT author_id, name FROM AUTHOR ORDER BY name'),
            rows('SELECT publisher_id, name FROM PUBLISHER ORDER BY name'),
            rows('SELECT category_id, name FROM CATEGORY ORDER BY name'))


def book_values(form):
    title = form.get('title', '').strip()
    if not title or len(title) > 200:
        raise ValueError('Book title is required (maximum 200 characters).')
    try:
        price = Decimal(form.get('price', '').strip())
        year = int(form.get('publish_year', '').strip())
        author_id = int(form.get('author_id', '').strip())
        publisher_id = int(form.get('publisher_id', '').strip())
        category_id = int(form.get('category_id', '').strip())
        if (not price.is_finite() or price < 0 or price > 99999999.99
                or not 1 <= year <= 2100 or min(author_id, publisher_id, category_id) < 1):
            raise ValueError()
    except (InvalidOperation, ValueError):
        raise ValueError('Enter a valid price, year and author/publisher/category.') from None
    return title, price, year, author_id, publisher_id, category_id


@app.route('/library/books/add', methods=['GET', 'POST'])
@app.route('/library/books/<int:book_id>/edit', methods=['GET', 'POST'])
def book_form(book_id=None):
    book = one('SELECT * FROM BOOK WHERE book_id = %s', (book_id,)) if book_id else None
    if book_id and book is None:
        abort(404)
    authors, publishers, categories = book_lists()
    if request.method == 'POST':
        try:
            values = book_values(request.form)
            if book_id:
                change('''UPDATE BOOK SET title=%s, price=%s, publish_year=%s,
                          author_id=%s, publisher_id=%s, category_id=%s WHERE book_id=%s''',
                       values + (book_id,))
            else:
                change('''INSERT INTO BOOK (title, price, publish_year, author_id,
                          publisher_id, category_id) VALUES (%s,%s,%s,%s,%s,%s)''', values)
            flash('Book saved.', 'success')
            return redirect(url_for('library'))
        except (ValueError, pymysql.err.IntegrityError) as exc:
            flash(str(exc) if isinstance(exc, ValueError) else 'Select existing author, publisher and category.', 'error')
            book = request.form
    return render_template('book_form.html', book=book, book_id=book_id,
                           authors=authors, publishers=publishers, categories=categories)


@app.route('/library/books/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    if not change('DELETE FROM BOOK WHERE book_id = %s', (book_id,)):
        abort(404)
    flash('Book deleted (including its loans).', 'success')
    return redirect(url_for('library'))


@app.route('/library/authors/add', methods=['GET', 'POST'])
@app.route('/library/authors/<int:author_id>/edit', methods=['GET', 'POST'])
def author_form(author_id=None):
    author = one('SELECT * FROM AUTHOR WHERE author_id = %s', (author_id,)) if author_id else None
    if author_id and author is None:
        abort(404)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        country = request.form.get('country', '').strip()
        if not name or not country or len(name) > 100 or len(country) > 50:
            flash('Name and country are required (max 100 and 50 characters).', 'error')
            author = request.form
        else:
            if author_id:
                change('UPDATE AUTHOR SET name=%s, country=%s WHERE author_id=%s',
                       (name, country, author_id))
            else:
                change('INSERT INTO AUTHOR (name, country) VALUES (%s,%s)', (name, country))
            flash('Author saved.', 'success')
            return redirect(url_for('library'))
    return render_template('author_form.html', author=author, author_id=author_id)


@app.route('/library/authors/<int:author_id>/delete', methods=['POST'])
def delete_author(author_id):
    if not change('DELETE FROM AUTHOR WHERE author_id = %s', (author_id,)):
        abort(404)
    flash('Author deleted (including their books and loans).', 'success')
    return redirect(url_for('library'))


@app.errorhandler(pymysql.MySQLError)
def database_error(error):
    app.logger.error('MySQL request failed: %s', error)
    return render_template('error.html', title='Database connection or query error',
                           message='Check MySQL is running, import the DDL and DML scripts, '
                                   'and set your credentials in website/.env.'), 503


@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', title='Page not found',
                           message='This page or record does not exist.'), 404


if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)

# Database Lab 4 — Part II (Problem 2): Library

A simple Flask + MySQL website for the **six Lab 4 Part II requirements (F2.1–F2.6)**. It extends the **Lab 3** `AUTHOR` and `BOOK` tables from the files supplied for this update. The original four authors and eight books are still present in the new seed data.

## Team (as in the supplied Lab 3 README)

- Mohamed hassan elragal — 2304246
- Mohamed Ashraf kamel — 2304059

## What's in this folder

```text
lab4-part2-library/
├── problem2_DDL.sql       six tables + primary/foreign keys + cascade deletes
├── problem2_DML.sql       sample data for all six tables
├── problem2_Queries.sql   all F2.1-F2.6 SQL queries, with comments
├── README.md              these instructions
├── .gitignore             ignores .env and temporary files
└── website/
    ├── app.py             Flask website routes and parameterized SQL
    ├── requirements.txt   Python packages
    ├── .env.example       copy to .env and set your MySQL password
    ├── templates/         HTML pages
    ├── static/style.css   one responsive stylesheet
    └── tests/test_sql.py  checks seed data, queries and cascades
```

## Run it step by step

**Requirements:** Python 3.10 or newer, MySQL Server 8, and MySQL Workbench (optional). The SQL creates a database called `library`.

**1. Import the SQL.** In MySQL Workbench, open and execute the following files **in this exact order**:

1. `problem2_DDL.sql` — creates the `library` database with six tables.
2. `problem2_DML.sql` — inserts the example records.
3. `problem2_Queries.sql` — optional: executes all Lab 4 queries and displays their results.

Alternative from a terminal in the project root:

```bash
mysql -u root -p < problem2_DDL.sql
mysql -u root -p < problem2_DML.sql
mysql -u root -p < problem2_Queries.sql
```

> **Important:** `problem2_DDL.sql` begins with `DROP DATABASE IF EXISTS library` and **deletes existing library data each time it is run**. Do not re-run the DDL if you need to preserve data. The DML is intended to be run once, after the DDL.

**2. Install and configure the website.** Open the whole project folder in Visual Studio Code, open a terminal and type:

```bash
cd website
python -m pip install -r requirements.txt
```

Create `website/.env` as a copy of `website/.env.example`. On Windows CMD:

```cmd
copy .env.example .env
```

On macOS/Linux:

```bash
cp .env.example .env
```

Edit `.env` and set **DB_PASSWORD** to your MySQL password. Leave `DB_USER=root` unless you use a different MySQL account. Set `SECRET_KEY` to a long random string. Do not upload `.env` to GitHub.

**3. Start the site.** In the `website` directory:

```bash
python app.py
```

Open **http://127.0.0.1:5000** in a browser. Use the tabs at the top to open the six pages. The **Manage** tab provides optional basic add/edit/delete pages for books and authors.

## Lab 4 Part II requirements

| Requirement | Page | URL | SQL concept |
|---|---|---|---|
| F2.1 | Search books by title, price and category | `/search` | `WHERE`, `LIKE`, `BETWEEN`, `ORDER BY` |
| F2.2 | Catalogue with author/publisher/category names | `/catalogue` | `JOIN` |
| F2.3 | Counts, average and min/max/total prices | `/reports` | `GROUP BY`, `HAVING`, aggregates |
| F2.4 | Open loans, members with no loans, unborrowed books | `/loans` | `JOIN`, `LEFT JOIN` |
| F2.5 | Three most borrowed books and top borrower | `/most-borrowed` | `GROUP BY`, `ORDER BY`, `LIMIT` |
| F2.6 | All author counts and same-country books | `/authors-and-books` | `LEFT JOIN`, `JOIN` |

**Bonus:** F2.1 website search uses safe `%s` parameters with PyMySQL; typed input is never inserted into the SQL code itself. `problem2_Queries.sql` uses MySQL `@variables` so the same search can also be run from Workbench. Edit the four variables near F2.1 to try different filters.

### Data requirements satisfied

- 5 authors (two from Egypt, one with **zero books**), 4 publishers, 3 categories.
- 10 books (original 8 kept, multiple books per author, **one never borrowed**, prices in the requested range).
- 6 members (**one with no loans**); 14 loans (including **not-returned loans**).
- Author deletion cascades to books; book deletion cascades to loans.
- The author and publisher of multiple books have the same country.

## Testing

Without starting MySQL, you can run a lightweight test of the schema relationships, example data and every query using Python's built-in SQLite:

```bash
python -m unittest discover -s tests -v
```

This test checks SQL logic and cascade behavior, but it is **not** a substitute for testing the actual MySQL Server and Flask website. To verify the full system, follow the setup above and click through all six pages.

## Scope / notes

- This ZIP contains **Lab 4 Part II / Problem 2 only**, as requested. It does **not** include Problem 1's `problem1_DDL.sql`, `problem1_DML.sql` or `problem1_Answers.txt`.
- The original upload included the Lab 3 README and SQL scripts but **not** the actual Lab 3 `website/` folder. A clean Flask implementation is therefore included. It has the six new Part II pages and basic Lab 3 book/author management, but **does not recreate** the old Lab 2 login/to-do system or Lab 3 image-upload bonus.
- The old `AUTHOR.photo` and `BOOK.cover` columns remain in the database to avoid dropping the supplied Lab 3 fields.
- Before submitting to GitHub, rename the folder to `lab4-<student-id>` as requested by the assignment (replace `<student-id>` with the submitting student's actual ID).
- No database password is included. `.env.example` only has placeholder credentials.

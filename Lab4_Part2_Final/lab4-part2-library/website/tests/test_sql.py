"""Run without MySQL or third-party Python packages: SQL logic smoke checks.

SQLite is used only for portability of the SELECT queries / foreign keys.
The submission SQL is intended for MySQL 8 and should also be run there.
"""
import re
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def example_db():
    ddl = (ROOT / 'problem2_DDL.sql').read_text(encoding='utf8')
    dml = (ROOT / 'problem2_DML.sql').read_text(encoding='utf8')
    # Translate MySQL-only setup/auto-increment syntax for in-memory SQLite.
    ddl = re.sub(r'(?m)^\s*(?:DROP DATABASE|CREATE DATABASE|USE library).*?;\s*$', '', ddl)
    ddl = re.sub(r'\bINT NOT NULL AUTO_INCREMENT\b', 'INTEGER PRIMARY KEY AUTOINCREMENT', ddl)
    ddl = re.sub(r'(?m)^\s*PRIMARY KEY \([^)]+\),?\s*$', '', ddl)
    # Auto-increment id columns became primary keys; previous lines may end with a comma.
    ddl = re.sub(r'(INTEGER PRIMARY KEY AUTOINCREMENT),\s*\n\s*\)', r'\1\n)', ddl)
    ddl = re.sub(r',\s*\n(\s*\))', r'\n\1', ddl)
    ddl = ddl.replace('ENGINE=InnoDB', '')
    dml = re.sub(r'(?m)^\s*USE library;\s*$', '', dml)
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    conn.executescript(ddl)
    conn.executescript(dml)
    return conn


def query_sections():
    text = (ROOT / 'problem2_Queries.sql').read_text(encoding='utf8')
    sections = {}
    heading = None
    sql = []
    for line in text.splitlines():
        tag = re.match(r'^-- (F2\.\d(?:\([abc]\))?)(?:\s|$)', line)
        if tag:
            if heading is not None:
                sections[heading] = '\n'.join(sql).strip()
            heading, sql = tag.group(1), []
        elif heading is not None and not line.lstrip().startswith('--'):
            sql.append(line)
    if heading is not None:
        sections[heading] = '\n'.join(sql).strip()
    return sections


class Lab4SQLTests(unittest.TestCase):
    def setUp(self):
        self.conn = example_db()

    def tearDown(self):
        self.conn.close()

    def test_table_counts_and_examples(self):
        wanted = {'AUTHOR': 5, 'PUBLISHER': 4, 'CATEGORY': 3,
                  'BOOK': 10, 'MEMBER': 6, 'LOAN': 14}
        for table, count in wanted.items():
            actual = self.conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
            self.assertEqual(actual, count, table)
        self.assertIsNone(self.conn.execute('SELECT return_date FROM LOAN WHERE loan_id=4').fetchone()[0])

    def test_every_deliverable_query_runs(self):
        sections = query_sections()
        self.assertEqual(len(sections), 12, list(sections))
        for label, content in sections.items():
            sql = re.sub(r'(?m)^SET [^\n]*\n?', '', content).strip()
            sql = sql.replace("CONCAT('%', @title_keyword, '%')", "'%' || @title_keyword || '%'")
            params = {'title_keyword': '', 'minimum_price': 0,
                      'maximum_price': 100000, 'category_id': None}
            try:
                result = self.conn.execute(sql, params).fetchall()
            except Exception as exc:
                self.fail(f'{label} failed: {exc} / SQL: {sql}')
            self.assertIsInstance(result, list, label)
        self.assertEqual(set(sections), {
            'F2.1', 'F2.2', 'F2.3(a)', 'F2.3(b)', 'F2.3(c)',
            'F2.4(a)', 'F2.4(b)', 'F2.4(c)', 'F2.5(a)',
            'F2.5(b)', 'F2.6(a)', 'F2.6(b)'})

    def test_required_results(self):
        self.assertEqual(self.conn.execute('''
            SELECT m.name FROM MEMBER m LEFT JOIN LOAN l ON m.member_id=l.member_id
            WHERE l.loan_id IS NULL''').fetchone()[0], 'Nour Tarek')
        self.assertEqual(self.conn.execute('''
            SELECT b.title FROM BOOK b LEFT JOIN LOAN l ON b.book_id=l.book_id
            WHERE l.loan_id IS NULL''').fetchone()[0], 'The Secret Adversary')
        self.assertEqual(self.conn.execute('''
            SELECT a.name FROM AUTHOR a LEFT JOIN BOOK b ON a.author_id=b.author_id
            GROUP BY a.author_id HAVING COUNT(b.book_id)=0''').fetchone()[0], 'Tawfiq al-Hakim')
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM LOAN WHERE return_date IS NULL').fetchone()[0], 5)
        self.assertEqual(self.conn.execute('''
            SELECT name FROM MEMBER m JOIN LOAN l ON m.member_id=l.member_id
            GROUP BY m.member_id ORDER BY COUNT(l.loan_id) DESC LIMIT 1''').fetchone()[0], 'Omar Ahmed')
        self.assertEqual(len(self.conn.execute('''
            SELECT title FROM BOOK WHERE title LIKE ? AND price BETWEEN ? AND ?
            AND category_id=?''', ('%Palace%', 15, 20, 3)).fetchall()), 1)

    def test_author_deletion_cascades_books_and_loans(self):
        loans_before = self.conn.execute('SELECT COUNT(*) FROM LOAN').fetchone()[0]
        removed = self.conn.execute('SELECT COUNT(*) FROM BOOK WHERE author_id=1').fetchone()[0]
        self.assertEqual(removed, 3)
        self.conn.execute('DELETE FROM AUTHOR WHERE author_id=1')
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM BOOK WHERE author_id=1').fetchone()[0], 0)
        self.assertLess(self.conn.execute('SELECT COUNT(*) FROM LOAN').fetchone()[0], loans_before)


    def test_all_app_sql_syntax(self):
        """Check every SQL statement authored in the Flask app using SQLite EXPLAIN."""
        import ast
        source = (ROOT / 'website' / 'app.py').read_text(encoding='utf8')
        tree = ast.parse(source)
        checked = 0
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id in ('rows', 'one', 'change') and node.args):
                sql = node.args[0]
                if not isinstance(sql, ast.Constant) or not isinstance(sql.value, str):
                    continue
                statement = sql.value.replace('%s', '?')
                bindings = [1] * statement.count('?')
                try:
                    self.conn.execute('EXPLAIN ' + statement, bindings).fetchall()
                except Exception as exc:
                    self.fail(f'App SQL invalid ({node.func.id}): {exc}; SQL = {statement}')
                checked += 1
        self.assertGreaterEqual(checked, 24)

    def test_book_deletion_cascades_loans(self):
        self.conn.execute('DELETE FROM BOOK WHERE book_id=3')
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM LOAN WHERE book_id=3').fetchone()[0], 0)


if __name__ == '__main__':
    unittest.main()

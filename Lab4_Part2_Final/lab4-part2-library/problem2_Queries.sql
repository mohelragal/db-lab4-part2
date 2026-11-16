-- Lab 4 - Part II, Problem 2. Run AFTER DDL and DML in MySQL Workbench.
USE library;

-- F2.1 Search books (edit these four variables and re-run this section).
SET @title_keyword = '';
SET @minimum_price = 0;
SET @maximum_price = 100000;
SET @category_id = NULL; -- NULL = all categories; use 1, 2 or 3 to filter
SELECT b.book_id, b.title, b.price, c.name AS category
FROM BOOK AS b
JOIN CATEGORY AS c ON b.category_id = c.category_id
WHERE b.title LIKE CONCAT('%', @title_keyword, '%')
  AND b.price BETWEEN @minimum_price AND @maximum_price
  AND (@category_id IS NULL OR b.category_id = @category_id)
ORDER BY b.price ASC, b.title ASC;

-- F2.2 Catalogue: show names rather than IDs.
SELECT b.book_id, b.title, b.price, b.publish_year,
       a.name AS author, p.name AS publisher, c.name AS category
FROM BOOK AS b
JOIN AUTHOR AS a ON b.author_id = a.author_id
JOIN PUBLISHER AS p ON b.publisher_id = p.publisher_id
JOIN CATEGORY AS c ON b.category_id = c.category_id
ORDER BY b.title;

-- F2.3(a) Number of books and average price in each category.
SELECT c.name AS category, COUNT(b.book_id) AS book_count,
       AVG(b.price) AS average_price
FROM CATEGORY AS c
LEFT JOIN BOOK AS b ON c.category_id = b.category_id
GROUP BY c.category_id, c.name
ORDER BY c.name;

-- F2.3(b) Authors with at least 2 books.
SELECT a.name AS author, COUNT(b.book_id) AS book_count
FROM AUTHOR AS a
JOIN BOOK AS b ON a.author_id = b.author_id
GROUP BY a.author_id, a.name
HAVING COUNT(b.book_id) >= 2
ORDER BY book_count DESC, a.name;

-- F2.3(c) Whole library price total, minimum, maximum.
SELECT SUM(price) AS total_price, MIN(price) AS minimum_price,
       MAX(price) AS maximum_price
FROM BOOK;

-- F2.4(a) Loans that are not returned.
SELECT l.loan_id, b.title AS book, m.name AS member,
       l.loan_date, l.return_date
FROM LOAN AS l
JOIN BOOK AS b ON l.book_id = b.book_id
JOIN `MEMBER` AS m ON l.member_id = m.member_id
WHERE l.return_date IS NULL
ORDER BY l.loan_date;

-- F2.4(b) Members who have no loans.
SELECT m.member_id, m.name, m.email
FROM `MEMBER` AS m
LEFT JOIN LOAN AS l ON m.member_id = l.member_id
WHERE l.loan_id IS NULL
ORDER BY m.name;

-- F2.4(c) Books that were never borrowed.
SELECT b.book_id, b.title
FROM BOOK AS b
LEFT JOIN LOAN AS l ON b.book_id = l.book_id
WHERE l.loan_id IS NULL
ORDER BY b.title;

-- F2.5(a) Top 3 books by loan count.
SELECT b.book_id, b.title, COUNT(l.loan_id) AS loan_count
FROM BOOK AS b
LEFT JOIN LOAN AS l ON b.book_id = l.book_id
GROUP BY b.book_id, b.title
ORDER BY loan_count DESC, b.title
LIMIT 3;

-- F2.5(b) Member who borrowed the most books.
SELECT m.member_id, m.name, COUNT(l.loan_id) AS loan_count
FROM `MEMBER` AS m
LEFT JOIN LOAN AS l ON m.member_id = l.member_id
GROUP BY m.member_id, m.name
ORDER BY loan_count DESC, m.name
LIMIT 1;

-- F2.6(a) All authors, including authors with zero books.
SELECT a.author_id, a.name, COUNT(b.book_id) AS book_count
FROM AUTHOR AS a
LEFT JOIN BOOK AS b ON a.author_id = b.author_id
GROUP BY a.author_id, a.name
ORDER BY a.name;

-- F2.6(b) Books whose author and publisher are from the same country.
SELECT b.title, a.name AS author, p.name AS publisher, a.country
FROM BOOK AS b
JOIN AUTHOR AS a ON b.author_id = a.author_id
JOIN PUBLISHER AS p ON b.publisher_id = p.publisher_id
WHERE a.country = p.country
ORDER BY b.title;

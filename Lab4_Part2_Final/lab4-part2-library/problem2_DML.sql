-- Lab 4 - Part II, Problem 2 seed data.
-- Run once AFTER problem2_DDL.sql. Preserves the original 4 authors / 8 books.
USE library;

INSERT INTO AUTHOR (author_id, name, country) VALUES
(1, 'Naguib Mahfouz', 'Egypt'),
(2, 'Agatha Christie', 'United Kingdom'),
(3, 'Gabriel Garcia Marquez', 'Colombia'),
(4, 'Haruki Murakami', 'Japan'),
(5, 'Tawfiq al-Hakim', 'Egypt'); -- author with no books

INSERT INTO PUBLISHER (publisher_id, name, country) VALUES
(1, 'Cairo House', 'Egypt'),
(2, 'London Books', 'United Kingdom'),
(3, 'Bogota Press', 'Colombia'),
(4, 'Tokyo Editions', 'Japan');

INSERT INTO CATEGORY (category_id, name) VALUES
(1, 'Literary Fiction'),
(2, 'Mystery'),
(3, 'Classics');

INSERT INTO BOOK (book_id, title, price, publish_year, author_id, publisher_id, category_id) VALUES
(1, 'Palace Walk',                   15.50, 1956, 1, 1, 3),
(2, 'Children of the Alley',         12.00, 1959, 1, 1, 3),
(3, 'Murder on the Orient Express',  18.75, 1934, 2, 2, 2),
(4, 'And Then There Were None',      16.00, 1939, 2, 2, 2),
(5, 'One Hundred Years of Solitude', 20.00, 1967, 3, 3, 1),
(6, 'Love in the Time of Cholera',   17.25, 1985, 3, 3, 1),
(7, 'Norwegian Wood',                14.90, 1987, 4, 4, 1),
(8, 'Kafka on the Shore',            19.50, 2002, 4, 4, 1),
(9, 'The Thief and the Dogs',        13.75, 1961, 1, 1, 3),
(10, 'The Secret Adversary',         11.50, 1922, 2, 2, 2); -- never borrowed

INSERT INTO `MEMBER` (member_id, name, email, join_date) VALUES
(1, 'Omar Ahmed', 'omar@example.com', '2026-09-01'),
(2, 'Sara Ali', 'sara@example.com', '2026-09-02'),
(3, 'Laila Hassan', 'laila@example.com', '2026-09-03'),
(4, 'Karim Adel', 'karim@example.com', '2026-09-04'),
(5, 'Mona Said', 'mona@example.com', '2026-09-05'),
(6, 'Nour Tarek', 'nour@example.com', '2026-09-06'); -- no loans

INSERT INTO LOAN (loan_id, book_id, member_id, loan_date, return_date) VALUES
(1, 1, 1, '2026-09-10', '2026-09-17'),
(2, 2, 2, '2026-09-11', '2026-09-20'),
(3, 3, 1, '2026-09-12', '2026-09-19'),
(4, 4, 3, '2026-09-14', NULL),
(5, 5, 4, '2026-09-15', '2026-09-25'),
(6, 6, 1, '2026-09-18', NULL),
(7, 7, 2, '2026-09-20', '2026-09-28'),
(8, 8, 5, '2026-09-21', '2026-09-29'),
(9, 1, 3, '2026-10-01', NULL),
(10, 3, 1, '2026-10-02', '2026-10-09'),
(11, 5, 2, '2026-10-03', NULL),
(12, 9, 4, '2026-10-04', '2026-10-12'),
(13, 1, 1, '2026-10-15', '2026-10-23'),
(14, 3, 5, '2026-10-16', NULL);

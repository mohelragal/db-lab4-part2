-- Lab 4 - Part II, Problem 2. Re-runnable MySQL 8 script.
-- Recreates ONLY the library database. Existing library data will be lost.
DROP DATABASE IF EXISTS library;
CREATE DATABASE library CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE library;

-- Keep the Lab 3 photo/cover columns for compatibility.
CREATE TABLE AUTHOR (
    author_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50) NOT NULL,
    photo VARCHAR(255) NULL,
    PRIMARY KEY (author_id)
) ENGINE=InnoDB;

CREATE TABLE PUBLISHER (
    publisher_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50) NOT NULL,
    PRIMARY KEY (publisher_id)
) ENGINE=InnoDB;

CREATE TABLE CATEGORY (
    category_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    PRIMARY KEY (category_id)
) ENGINE=InnoDB;

CREATE TABLE BOOK (
    book_id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    publish_year INT NOT NULL,
    author_id INT NOT NULL,
    publisher_id INT NOT NULL,
    category_id INT NOT NULL,
    cover VARCHAR(255) NULL,
    PRIMARY KEY (book_id),
    FOREIGN KEY (author_id) REFERENCES AUTHOR (author_id) ON DELETE CASCADE,
    FOREIGN KEY (publisher_id) REFERENCES PUBLISHER (publisher_id),
    FOREIGN KEY (category_id) REFERENCES CATEGORY (category_id)
) ENGINE=InnoDB;

CREATE TABLE `MEMBER` (
    member_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    join_date DATE NOT NULL,
    PRIMARY KEY (member_id)
) ENGINE=InnoDB;

CREATE TABLE LOAN (
    loan_id INT NOT NULL AUTO_INCREMENT,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    loan_date DATE NOT NULL,
    return_date DATE NULL,
    PRIMARY KEY (loan_id),
    FOREIGN KEY (book_id) REFERENCES BOOK (book_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES `MEMBER` (member_id)
) ENGINE=InnoDB;

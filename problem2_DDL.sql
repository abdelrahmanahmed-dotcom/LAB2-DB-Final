-- Lab 3, Problem 2: the library database (DDL).
-- Re-runnable: it drops and recreates the database every time.
--   mysql -u root -p < problem2_DDL.sql

DROP DATABASE IF EXISTS library;
CREATE DATABASE library;
USE library;

-- AUTHOR must exist before BOOK can point at it.
CREATE TABLE author (
    author_id INT          NOT NULL AUTO_INCREMENT,
    name      VARCHAR(100) NOT NULL,
    country   VARCHAR(50)  NOT NULL,
    image     VARCHAR(255) NULL,       -- [Bonus] file name of the author's photo (NULL = no photo)
    PRIMARY KEY (author_id)
);

CREATE TABLE book (
    book_id   INT           NOT NULL AUTO_INCREMENT,
    title     VARCHAR(200)  NOT NULL,
    price     DECIMAL(10,2) NOT NULL,
    author_id INT           NOT NULL,
    image     VARCHAR(255)  NULL,      -- [Bonus] file name of the book cover (NULL = no cover)
    PRIMARY KEY (book_id),
    -- When an author is deleted, all the books of that author are deleted too.
    CONSTRAINT fk_book_author
        FOREIGN KEY (author_id) REFERENCES author (author_id)
        ON DELETE CASCADE
);

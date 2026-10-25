-- Lab 3, Problem 2: seed data (4 authors, 8 books).
--   mysql -u root -p < problem2_DML.sql
-- Run problem2_DDL.sql first.
USE library;

INSERT INTO author (author_id, name, country) VALUES
(1, 'Naguib Mahfouz',   'Egypt'),
(2, 'Agatha Christie',  'United Kingdom'),
(3, 'Gabriel Garcia Marquez', 'Colombia'),
(4, 'Taha Hussein',     'Egypt');

INSERT INTO book (book_id, title, price, author_id) VALUES
(1, 'Palace Walk',                         180.00, 1),
(2, 'Children of the Alley',               150.50, 1),
(3, 'Murder on the Orient Express',        210.00, 2),
(4, 'And Then There Were None',            195.75, 2),
(5, 'One Hundred Years of Solitude',       260.00, 3),
(6, 'Love in the Time of Cholera',         240.00, 3),
(7, 'The Days',                            120.00, 4),
(8, 'The Future of Culture in Egypt',      135.25, 4);

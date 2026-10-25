-- Lab 3, Problem 1: seed data (3+ rows in every table).
--   mysql -u root -p < problem1_DML.sql
-- Run problem1_DDL.sql first.
USE company;

-- 1) Employees first, without a department yet (Dno is NULL for now).
INSERT INTO employee (ssn, fname, lname, bdate, address, gender, salary, Dno) VALUES
('100000001', 'Ahmed',   'Hassan',  '1985-03-12', 'Smouha, Alexandria',     'M', 18000.00, NULL),
('100000002', 'Mona',    'Said',    '1988-07-25', 'Maadi, Cairo',           'F', 16500.00, NULL),
('100000003', 'Omar',    'Khaled',  '1990-11-02', 'Nasr City, Cairo',       'M', 14000.00, NULL),
('100000004', 'Salma',   'Adel',    '1993-01-18', 'Sidi Gaber, Alexandria', 'F',  9500.00, NULL),
('100000005', 'Youssef', 'Ali',     '1995-09-30', 'Mansoura, Dakahlia',     'M',  8800.00, NULL),
('100000006', 'Nour',    'Ibrahim', '1997-05-14', 'Dokki, Giza',            'F',  8200.00, NULL);

-- 2) Departments: each manager already exists in EMPLOYEE.
INSERT INTO department (Dnumber, Dname, mgr_ssn, mgr_start_date) VALUES
(1, 'Engineering',    '100000001', '2020-01-15'),
(2, 'Research',       '100000002', '2021-06-01'),
(3, 'Administration', '100000003', '2019-09-10');

-- 3) Now the departments exist: give every employee a department.
UPDATE employee SET Dno = 1 WHERE ssn IN ('100000001', '100000004');
UPDATE employee SET Dno = 2 WHERE ssn IN ('100000002', '100000005');
UPDATE employee SET Dno = 3 WHERE ssn IN ('100000003', '100000006');

-- 4) Projects (each one belongs to an existing department).
INSERT INTO project (Pnumber, Pname, Plocation, Dno) VALUES
(1, 'ProductX',        'Alexandria', 1),
(2, 'ProductY',        'Cairo',      2),
(3, 'Computerization', 'Giza',       3);

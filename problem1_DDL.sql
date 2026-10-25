-- Lab 3, Problem 1: the COMPANY database (DDL).
-- Re-runnable: it drops and recreates the database every time.
--   mysql -u root -p < problem1_DDL.sql

DROP DATABASE IF EXISTS company;
CREATE DATABASE company;
USE company;

-- EMPLOYEE is created first. Its foreign key (Dno -> DEPARTMENT) is added at the
-- end with ALTER TABLE, because DEPARTMENT does not exist yet and DEPARTMENT
-- points back to EMPLOYEE (a circular reference).
CREATE TABLE employee (
    ssn      CHAR(9)       NOT NULL,
    fname    VARCHAR(30)   NOT NULL,
    lname    VARCHAR(30)   NOT NULL,
    bdate    DATE,
    address  VARCHAR(100),
    gender   CHAR(1),
    salary   DECIMAL(10,2),
    Dno      INT,                      -- NULL allowed: see Q1.3
    PRIMARY KEY (ssn)
);

CREATE TABLE department (
    Dnumber        INT         NOT NULL,
    Dname          VARCHAR(50) NOT NULL,
    mgr_ssn        CHAR(9),            -- NULL allowed: see Q1.3
    mgr_start_date DATE,
    PRIMARY KEY (Dnumber),
    CONSTRAINT fk_department_mgr
        FOREIGN KEY (mgr_ssn) REFERENCES employee (ssn)
);

CREATE TABLE project (
    Pnumber   INT         NOT NULL,
    Pname     VARCHAR(50) NOT NULL,
    Plocation VARCHAR(50),
    Dno       INT         NOT NULL,
    PRIMARY KEY (Pnumber),
    CONSTRAINT fk_project_dept
        FOREIGN KEY (Dno) REFERENCES department (Dnumber)
);

-- Now DEPARTMENT exists, so EMPLOYEE can point at it.
ALTER TABLE employee
    ADD CONSTRAINT fk_employee_dept
    FOREIGN KEY (Dno) REFERENCES department (Dnumber);

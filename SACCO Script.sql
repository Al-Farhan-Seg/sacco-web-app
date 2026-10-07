CREATE DATABASE SACCO;
USE SACCO;
show tables;
CREATE TABLE MEMBER(
	member_id INT(1) AUTO_INCREMENT PRIMARY KEY NOT NULL,
	First_name VARCHAR(100) NOT NULL,
    Last_name VARCHAR(100) NOT NULL,
    Contact int(10) NOT NULL,
	Address VARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL
);

alter table MEMBER
	ADD Gender CHAR(2) NOT NULL;
alter table MEMBER modify column Gender ENUM ('F','M'); 
alter table MEMBER modify column Contact char(10);

DESCRIBE MEMBER;


CREATE TABLE ACCOUNT(
	Account_id INT  PRIMARY KEY NOT NULL,
	member_id INT NOT NULL,
    Account_No int(10) NOT NULL,
    Account_type VARCHAR(20) NOT NULL,
    Balance INT NOT NULL,
	FOREIGN KEY (member_id) REFERENCES MEMBER(member_id) 
);

 DESCRIBE ACCOUNT;
 
 CREATE TABLE LOAN(
	Loan_id INT PRIMARY KEY NOT NULL,
	member_id INT NOT NULL,
	Staff_id INT NOT NULL,
    Loan_amount INT NOT NULL,
	payment_period VARCHAR(100) NOT NULL,
    payment_amount INT NOT NULL,
    FOREIGN KEY (member_id) REFERENCES MEMBER(member_id),
    FOREIGN KEY (Staff_id) REFERENCES STAFF(Staff_id)
);

 DESCRIBE LOAN;
 
 CREATE TABLE LOAN_PAYMENT(
	Payment_id INT PRIMARY KEY NOT NULL,
    Loan_id INT NOT NULL,
	Amount INT NOT NULL,
    Date DATE NOT NULL,
    FOREIGN KEY (Loan_id) REFERENCES LOAN(Loan_id)
);

 DESCRIBE LOAN_PAYMENT;
 
 CREATE TABLE SAVINGS(
	savings_id INT PRIMARY KEY NOT NULL,
    member_id INT NOT NULL,
	Account_id INT NOT NULL, 
    Staff_id INT NOT NULL,
    Amount INT NOT NULL,
    Date DATE NOT NULL,
	FOREIGN KEY (member_id) REFERENCES MEMBER(member_id),
	FOREIGN KEY (Staff_id) REFERENCES STAFF(Staff_id) 
);

 ALTER TABLE  SAVINGS ADD Payment_method VARCHAR(30) NOT NULL;
 DESCRIBE SAVINGS;

 
 CREATE TABLE STAFF(
	Staff_id INT PRIMARY KEY NOT NULL,
    First_name VARCHAR(100) NOT NULL,
    Last_name VARCHAR(100) NOT NULL,
    Contact int(10) NOT NULL,
	position VARCHAR(50) NOT NULL,
    Role VARCHAR(50)
);

alter table STAFF modify column Contact char(10);
alter table STAFF add column Gender enum('M','F');

DESCRIBE STAFF;

/* Removing unnecessary tables */
DROP TABLE PART_TIME_STAFF;
DROP TABLE FULL_TIME_STAFF;
DROP TABLE POSITION;
SHOW TABLES;

/*
CREATE TABLE POSITION (
	Position_id INT PRIMARY KEY NOT NULL,
    Staff_id INT NOT NULL,
	Name VARCHAR(50) NOT NULL,
    Responsibility VARCHAR(100) NOT NULL ,
	FOREIGN KEY (Staff_id) REFERENCES STAFF(Staff_id)
);
DESCRIBE POSITION;
*/
    

CREATE TABLE WITHDRAW(
	Withdraw_id INT PRIMARY KEY NOT NULL,
    Account_Id INT NOT NULL,
	member_id INT NOT NULL,
    Amount INT NOT NULL,
    Date DATE NOT NULL,
    FOREIGN KEY (member_id) REFERENCES MEMBER(member_id),
    FOREIGN KEY (Account_id) REFERENCES ACCOUNT(Account_id)
);
 ALTER TABLE WITHDRAW MODIFY COLUMN Amount varchar(100);
 
SHOW CREATE TABLE WITHDRAW;
alter table withdraw drop foreign key withdraw_ibfk_2;
alter table withdraw drop column account_id;

 DESCRIBE WITHDRAW;
 
 
 
 

-- INSERT DATA INTO MEMBER (Parent Table - 5 records)
INSERT INTO MEMBER (First_name, Last_name, Contact, Address, Email, Gender) VALUES
('MAHAD','BUGEMBE','0700000001','Kampala','mahad@gmail.com','M'),
('Sarah','Nam','0700000002','Entebbe','sarah@gmail.com','F'),
('Najib','Lwanga','0700000003','Jinja','najib@gmail.com','M'),
('FARHAN','SEGUJJA','0700000004','Mukono','farhan@gmail.com','M'),
('David','Okello','0700000005','Gulu','david@gmail.com','M');

-- INSERT DATA INTO STAFF (Parent Table - 5 records)
INSERT INTO STAFF (Staff_id, First_name, Last_name, Contact, position, Role, Gender) VALUES
(1,'James','Okumu','0710000001','Manager','Admin','M'),
(2,'Linda','Ayo','0710000002','Clerk','User','F'),
(3,'Peter','Musa','0710000003','Accountant','User','M'),
(4,'Grace','Nab','0710000004','Supervisor','Admin','F'),
(5,'Brian','Kato','0710000005','Officer','User','M');

-- INSERT DATA INTO ACCOUNT (Child - 10 records)
INSERT INTO ACCOUNT VALUES
(1,1,10001,'Savings',5000),
(2,1,10002,'Current',7000),
(3,2,10003,'Savings',3000),
(4,2,10004,'Current',4000),
(5,3,10005,'Savings',8000),
(6,3,10006,'Current',2000),
(7,1,10007,'Savings',6000),
(8,2,10008,'Current',3500),
(9,3,10009,'Savings',4500),
(10,4,10010,'Savings',9000);

-- INSERT DATA INTO LOAN (Multiple FK - 20 records)
INSERT INTO LOAN VALUES
(1,1,1,10000,'12 months',1000),
(2,2,2,20000,'10 months',2000),
(3,3,3,15000,'8 months',1800),
(4,1,2,12000,'6 months',2000),
(5,2,3,25000,'12 months',2100),
(6,3,1,18000,'9 months',1900),
(7,1,4,22000,'10 months',2200),
(8,2,5,16000,'8 months',1700),
(9,3,2,14000,'7 months',1600),
(10,1,3,30000,'12 months',2500),
(11,2,4,21000,'10 months',2000),
(12,3,5,19000,'9 months',1800),
(13,1,1,17000,'8 months',1700),
(14,2,2,23000,'11 months',2100),
(15,3,3,26000,'12 months',2200),
(16,1,4,28000,'12 months',2400),
(17,2,5,24000,'10 months',2000),
(18,3,1,20000,'9 months',1900),
(19,1,2,15000,'7 months',1600),
(20,2,3,18000,'8 months',1700);

-- INSERT DATA INTO LOAN_PAYMENT (Child - 10 records)
INSERT INTO LOAN_PAYMENT VALUES
(1,1,1000,'2024-01-01'),
(2,2,2000,'2024-01-02'),
(3,3,1500,'2024-01-03'),
(4,4,2000,'2024-01-04'),
(5,5,2100,'2024-01-05'),
(6,6,1900,'2024-01-06'),
(7,7,2200,'2024-01-07'),
(8,8,1700,'2024-01-08'),
(9,9,1600,'2024-01-09'),
(10,10,2500,'2024-01-10');

-- INSERT DATA INTO SAVINGS (Multiple FK - 20 records)
INSERT INTO SAVINGS VALUES
(1,1,1,1,1000,'2024-01-01','Cash'),
(2,2,3,2,1500,'2024-01-02','Mobile'),
(3,3,5,3,2000,'2024-01-03','Cash'),
(4,1,2,4,1200,'2024-01-04','Bank'),
(5,2,4,5,1300,'2024-01-05','Cash'),
(6,3,6,1,1400,'2024-01-06','Mobile'),
(7,1,7,2,1500,'2024-01-07','Cash'),
(8,2,8,3,1600,'2024-01-08','Bank'),
(9,3,9,4,1700,'2024-01-09','Cash'),
(10,1,10,5,1800,'2024-01-10','Mobile'),
(11,2,3,1,1900,'2024-01-11','Cash'),
(12,3,5,2,2000,'2024-01-12','Bank'),
(13,1,1,3,2100,'2024-01-13','Cash'),
(14,2,4,4,2200,'2024-01-14','Mobile'),
(15,3,6,5,2300,'2024-01-15','Cash'),
(16,1,7,1,2400,'2024-01-16','Bank'),
(17,2,8,2,2500,'2024-01-17','Cash'),
(18,3,9,3,2600,'2024-01-18','Mobile'),
(19,1,2,4,2700,'2024-01-19','Cash'),
(20,2,3,5,2800,'2024-01-20','Bank');

/*Display male members with their full contact details in alphabetical order*/
SELECT
    member_id,
    CONCAT(First_name, ' ', Last_name) AS Full_Name,
    Gender,
    Contact,
    Address,
    Email
FROM MEMBER
WHERE Gender = 'M'
ORDER BY First_name ASC, Last_name ASC;

/*Display number and percentage of members by gender*/
SELECT
    Gender,
    COUNT(*) AS Number_of_Members,
    ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM MEMBER)), 2) AS Percentage
FROM MEMBER
GROUP BY Gender;



/*Display savings made between two dates with saving category*/
SELECT
    savings_id,
    member_id,
    Account_id,
    Staff_id,
    Amount,
    Date,
    Payment_method,
    CASE
        WHEN Amount >= 2500 THEN 'Very High Saving'
        WHEN Amount >= 2000 THEN 'High Saving'
        WHEN Amount >= 1500 THEN 'Medium Saving'
        ELSE 'Low Saving'
    END AS Saving_Category
FROM SAVINGS
WHERE Date BETWEEN '2024-01-01' AND '2024-01-15'
ORDER BY Date ASC;

/* Retrieve loan applications and total loan amount per payment period */
SELECT 
    payment_period,
    COUNT(Loan_id) AS Loan_Applications,
    SUM(Loan_amount) AS Total_Loan_Amount,
    AVG(Loan_amount) AS Average_Loan_Amount
FROM LOAN
GROUP BY payment_period
ORDER BY Loan_Applications DESC;

/*Display accounts above 5000 with balance category*/
SELECT
    Account_id,
    member_id,
    Account_No,
    Account_type,
    Balance,
    CASE
        WHEN Balance >= 8000 THEN 'High Balance'
        WHEN Balance >= 6000 THEN 'Medium Balance'
        ELSE 'Low Balance'
    END AS Balance_Category
FROM ACCOUNT
WHERE Balance > 5000
ORDER BY Balance DESC;




/*            JOINS            */

/* Display members and their total savings */
SELECT 
    MEMBER.First_name,
    MEMBER.Last_name,
    SUM(SAVINGS.Amount) AS Total_Savings
FROM MEMBER
INNER JOIN SAVINGS
ON MEMBER.member_id = SAVINGS.member_id
GROUP BY MEMBER.member_id, MEMBER.First_name, MEMBER.Last_name;


/* Display loan details with member and staff */
SELECT 
    LOAN.Loan_id,
    MEMBER.First_name AS Member_Name,
    LOAN.Loan_amount,
    LOAN.payment_amount,
    STAFF.First_name AS Staff_Name
FROM LOAN
INNER JOIN MEMBER
ON MEMBER.member_id = LOAN.member_id
INNER JOIN STAFF
ON STAFF.Staff_id = LOAN.Staff_id;


/* Display all members and their loans, including members with no loan */
SELECT
    MEMBER.first_name,
    MEMBER.last_name,
    LOAN.loan_id,
    LOAN.loan_amount,
    LOAN.payment_amount,
    (LOAN.Loan_amount - LOAN.payment_amount) AS Loan_Balance
FROM MEMBER
LEFT JOIN LOAN
ON MEMBER.member_id = LOAN.member_id;








/*                SUB QUERIES                   */

/* Members with loan above average loan amount */
SELECT first_name, last_name
FROM MEMBER
WHERE member_id IN
(
SELECT member_id
FROM LOAN
WHERE Loan_amount >
	(
		SELECT AVG(Loan_amount)
		FROM LOAN
	)
);
/* Number of times each member has taken loans */
SELECT member_id,
(
SELECT COUNT(*)
FROM LOAN
WHERE LOAN.member_id=MEMBER.member_id
) AS Loan_Count
FROM MEMBER;

/* Retrieve savings records for female members */
SELECT *
FROM SAVINGS
WHERE member_id IN
(
SELECT member_id
FROM MEMBER
WHERE Gender='F'
);







/*               FUNCTIONS            */
/*Function to calculate total amount paid on a specific loan*/

DELIMITER $$

CREATE FUNCTION TotalLoanPaid(loanNumber INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE totalPaid INT;

    SELECT COALESCE(SUM(Amount), 0)
    INTO totalPaid
    FROM LOAN_PAYMENT
    WHERE Loan_id = loanNumber;

    RETURN totalPaid;
END $$

DELIMITER ;

/* Function test */
SELECT 
    Loan_id,
    Loan_amount,
    TotalLoanPaid(Loan_id) AS Total_Paid
FROM LOAN;

/*Function to calculate remaining loan balance using actual payments*/

DELIMITER $$

CREATE FUNCTION LoanBalance(loanNumber INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE loanAmount INT;
    DECLARE amountPaid INT;
    DECLARE balance INT;

    SELECT Loan_amount
    INTO loanAmount
    FROM LOAN
    WHERE Loan_id = loanNumber;

    SET amountPaid = TotalLoanPaid(loanNumber);

    SET balance = loanAmount - amountPaid;

    RETURN balance;
END $$

DELIMITER ;

/* Function test */
SELECT 
    Loan_id,
    Loan_amount,
    TotalLoanPaid(Loan_id) AS Total_Paid,
    LoanBalance(Loan_id) AS Remaining_Balance
FROM LOAN;



/*       STORED PROCEDURES     */

/* Procedure to record a saving and update account balance */

DELIMITER $$

CREATE PROCEDURE RecordSaving(
    IN memberNumber INT,
    IN accountNumber INT,
    IN staffNumber INT,
    IN savingAmount INT,
    IN savingDate DATE,
    IN paymentMethod VARCHAR(30)
)
BEGIN
    DECLARE newSavingId INT;

    SELECT MAX(savings_id) + 1
    INTO newSavingId
    FROM SAVINGS;

    INSERT INTO SAVINGS(savings_id, member_id, Account_id, Staff_id, Amount, Date, Payment_method)
    VALUES(newSavingId, memberNumber, accountNumber, staffNumber, savingAmount, savingDate, paymentMethod);

    UPDATE ACCOUNT
    SET Balance = Balance + savingAmount
    WHERE Account_id = accountNumber;
END $$

DELIMITER ;

CALL RecordSaving(1, 1, 1, 3000, '2024-02-01', 'Cash');


/* Procedure to record a loan payment and show remaining balance */

DELIMITER $$

CREATE PROCEDURE RecordLoanPayment(
    IN loanNumber INT,
    IN paymentAmount INT,
    IN paymentDate DATE
)
BEGIN
    DECLARE newPaymentId INT;

    SELECT MAX(Payment_id) + 1
    INTO newPaymentId
    FROM LOAN_PAYMENT;

    INSERT INTO LOAN_PAYMENT(Payment_id, Loan_id, Amount, Date)
    VALUES(newPaymentId, loanNumber, paymentAmount, paymentDate);

    SELECT
        LOAN.Loan_id,
        LOAN.Loan_amount,
        SUM(LOAN_PAYMENT.Amount) AS Total_Paid,
        LOAN.Loan_amount - SUM(LOAN_PAYMENT.Amount) AS Remaining_Balance
    FROM LOAN
    INNER JOIN LOAN_PAYMENT
    ON LOAN.Loan_id = LOAN_PAYMENT.Loan_id
    WHERE LOAN.Loan_id = loanNumber
    GROUP BY LOAN.Loan_id, LOAN.Loan_amount;
END $$

DELIMITER ;

CALL RecordLoanPayment(1, 500, '2024-02-01');


----------------------------------------------------------------





























/*           TRIGGERS      */
/*Trigger to automatically calculate savings tax*/
ALTER TABLE SAVINGS
ADD Tax DECIMAL(10,2);
DELIMITER $$

CREATE TRIGGER Savings_Tax
BEFORE INSERT ON SAVINGS
FOR EACH ROW
BEGIN
SET NEW.Tax = NEW.Amount * 0.05;
END $$

DELIMITER ;
/*Automatically update ACCOUNT balance after savings is inserted
Whenever a member makes a deposit in SAVINGS, the system should automatically:
increase their account balance in ACCOUNT*/
DELIMITER $$

CREATE TRIGGER update_account_balance
AFTER INSERT ON SAVINGS
FOR EACH ROW
BEGIN
    UPDATE ACCOUNT
    SET Balance = Balance + NEW.Amount
    WHERE member_id = NEW.member_id;
END $$

DELIMITER ;
INSERT INTO SAVINGS VALUES
(21,1,1,1,5000,'2024-01-21','Cash',1000);
INSERT INTO SAVINGS VALUES
(21,2,2,2,6000,'2024-01-21','Cash',2000);
SELECT * FROM ACCOUNT;

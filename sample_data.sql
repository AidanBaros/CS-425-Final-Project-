-- Table creation
CREATE TABLE Department (
    Dept_ID SERIAL PRIMARY KEY,
    Dept_Name VARCHAR(50) NOT NULL
);

CREATE TABLE Employee (
    Emp_ID SERIAL PRIMARY KEY,
    Fname VARCHAR(30),
    Lname VARCHAR(30),
    Salary NUMERIC(10,2),
    Dept_ID INT REFERENCES Department(Dept_ID)
);

-- Sample data
INSERT INTO Users (User_ID, User_Name, Email, User_Type) 
VALUES ('UUID','Tim','timEmail@email.com','Agent'),
	   ('UUID','Aidan','aidanEmail@email.com','Agent'),
	   ('UUID','Yousef','yousefEmail@email.com','Renter'),
	   ('UUID','Emily','emilyEmail@email.com','Renter');
	   
INSERT INTO Users_Addresses (User_Address_ID, User_ID, Address_ID) 
VALUES ('UUID','UUID_Tim','UUID_Address_Tim'),
	   ('UUID','UUID_Yousef','UUID_Address_Yousef'),
	   ('UUID','UUID_Emily','UUID_Address_Emily'),
	   ('UUID','UUID_Emily','UUID_Address_Emily1');

INSERT INTO Agents (Agent_ID, User_ID, Job_Title, Agency, Contact_Info) 
VALUES ('UUID','UUID_Tim','Senior Agent','Star Realtors','3168565619'),
	   ('UUID','UUID_Aidan','Senior Agent','Moon Realtors','3268565629');

INSERT INTO Renters (Renter_ID, User_ID, Move_In_Date, Pref_Location, Budget) 
VALUES ('UUID','UUID_Yousef','2025-12-01','Chicago','5000'),
	   ('UUID','UUID_Emily','2025-12-02','St. Louis','3200');





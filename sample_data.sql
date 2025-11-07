-- Sample data
-------------------------------------User & Location Data-----------------------------------------------
INSERT INTO Users (User_ID, User_Name, Email, User_Type) 
VALUES ('UUID','Tim','timEmail@email.com','Agent'),
	   ('UUID','Aidan','aidanEmail@email.com','Agent'),
	   ('UUID','Yousef','yousefEmail@email.com','Renter'),
	   ('UUID','Emily','emilyEmail@email.com','Renter');
	   
INSERT INTO Users_Addresses (User_Address_ID, User_ID, Address_ID) 
VALUES ('UUID','UUID_Tim','UUID_Address_Tim'),
	   ('UUID','UUID_Aidan','UUID_Address_Aidan'),
	   ('UUID','UUID_Yousef','UUID_Address_Yousef'),
	   ('UUID','UUID_Emily','UUID_Address_Emily'),
	   ('UUID','UUID_Emily','UUID_Address_Emily1');

INSERT INTO Agents (Agent_ID, User_ID, Job_Title, Agency, Contact_Info) 
VALUES ('UUID','UUID_Tim','Senior Agent','Star Realtors','3168565619'),
	   ('UUID','UUID_Aidan','Senior Agent','Moon Realtors','3268565629');

INSERT INTO Renters (Renter_ID, User_ID, Move_In_Date, Pref_Location, Budget) 
VALUES ('UUID','UUID_Yousef','2025-12-01','Chicago','5000'),
	   ('UUID','UUID_Emily','2025-12-02','St. Louis','3200');

INSERT INTO Card (Card_ID, Renter_ID, Address_ID, Card_Number, Expiration) 
VALUES ('UUID','UUID_Renter_Yousef','UUID_Address_Yousef','1234678221234123','05/28'),
	   ('UUID','UUID_Renter_Emily','UUID_Address_Emily','1334678221234123','07/29'),
	   ('UUID','UUID_Renter_Emily','UUID_Address_Emily1','1434678221234123','06/26');

INSERT INTO Locations (Location_ID, Address, City, State_, Country, Zip_Code) 
VALUES ('UUID','3303 s State st','Chicago','IL','United States','60616'),
	   ('UUID','3304 n State st','Chicago','IL','United States','60616'),
	   ('UUID','12678 Honeygrove ct','St. Louis','MO','United States','63146'),
	   ('UUID','2301 s State st','Chicago','IL','United States','60616'),
	   ('UUID','12768 Honeygrove ct','St. Louis','MO','United States','63146');
	   
-------------------------------------Property Data-----------------------------------------------

INSERT INTO Property (Property_ID, Type_, Location_ID, Description, Price, Availability, Crime_Rate) 
VALUES ('UUID','3303 s State st','Chicago','IL','United States','60616'),
	   ('UUID','3304 n State st','Chicago','IL','United States','60616'),
	   ('UUID','12678 Honeygrove ct','St. Louis','MO','United States','63146'),
	   ('UUID','2301 s State st','Chicago','IL','United States','60616'),
	   ('UUID','12768 Honeygrove ct','St. Louis','MO','United States','63146');





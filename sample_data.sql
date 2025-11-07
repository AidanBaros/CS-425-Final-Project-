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
VALUES ('UUID','House','UUID_Location','A fun place to live','400000','1','0.001'),
	   ('UUID','House','UUID_Location','A fun place to live','500000','1','0.0056'),
	   ('UUID','House','UUID_Location','A fun place to live','1000000','1','0.002'),
	   ('UUID','Apartment','UUID_Location','A fun place to rent','5000','1','0.001'),
	   ('UUID','Apartment','UUID_Location','A fun place to rent','750','0','0.1'),
	   ('UUID','Apartment','UUID_Location','A fun place to rent','1500','1','0.045'),
	   ('UUID','Commercial Building','UUID_Location','A fun place to work','55000','1','0.0001'),
	   ('UUID','Land','UUID_Location','A fun place to build','2000000','1','0.00001'),
	   ('UUID','Vacation Home','UUID_Location','A fun place to relax','5000000','0','0.000001'),
	   
INSERT INTO Booking (Booking_ID, Card_ID, Property_ID, Renter_ID, Agent_ID, Start_Date, End_Date) 
VALUES ('UUID','UUID_Card','UUID_Property','UUID_Agent_Tim','UUID_Renter_Emily','2026-03-12','2027-3-15'),
	   ('UUID','UUID_Card','UUID_Property','UUID_Agent_Tim','UUID_Renter_Emily','2026-06-12','2027-6-11'),
	   ('UUID','UUID_Card','UUID_Property','UUID_Agent_Aidan','UUID_Renter_Yousef','2026-09-12','2027-9-10');

INSERT INTO House (House_ID, Property_ID, Num_Rooms, Sq_Footage) 
VALUES ('UUID','UUID_Property','3','1900'),
	   ('UUID','UUID_Property','4','2100'),
	   ('UUID','UUID_Property','7','4000');

INSERT INTO Apartment (Apartment_ID, Property_ID, Num_Rooms, Sq_Footage, Building_Type) 
VALUES ('UUID','UUID_Property','2','750','Studio'),
	   ('UUID','UUID_Property','3','1500','Condo'),
	   ('UUID','UUID_Property','5','3000','Penthouse');

INSERT INTO Commercial_Buildings (Commercial_ID, Property_ID, Sq_Footage, Business_Type) 
VALUES ('UUID','UUID_Property','35000','Bank'),
	   ('UUID','UUID_Property','3','27000','Law Firm'),
	   ('UUID','UUID_Property','5','30000','Hardware Store');

INSERT INTO Land (Land_ID, Property_ID) 
VALUES ('UUID','UUID_Property'),
	   ('UUID','UUID_Property'),
	   ('UUID','UUID_Property');

INSERT INTO Vacation_Home (Vacation_ID, Property_ID) 
VALUES ('UUID','UUID_Property'),
	   ('UUID','UUID_Property'),
	   ('UUID','UUID_Property');
	   
INSERT INTO School (School_ID, Property_ID, School_Name, School_Address) 
VALUES ('UUID','UUID_Property','Parkway North','106 S FeeFee ln'),
	   ('UUID','UUID_Property','Parkway South','66 N FeeFee dr'),
	   ('UUID','UUID_Property','Parkway East','56 S FeeFee dr');


		





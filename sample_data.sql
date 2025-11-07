-------------------------------------User & Location Data-----------------------------------------------
INSERT INTO Users (User_ID, User_Name, Email, User_Type) 
VALUES ('U001','Tim','timEmail@email.com','Agent'),
	   ('U002','Aidan','aidanEmail@email.com','Agent'),
	   ('U003','Yousef','yousefEmail@email.com','Renter'),
	   ('U004','Emily','emilyEmail@email.com','Renter');
	   
INSERT INTO Users_Addresses (User_Address_ID, User_ID, Address_ID) 
VALUES ('UA001','U001','AD001'),
	   ('UA002','U002','AD002'),
	   ('UA003','U003','AD003'),
	   ('UA004','U004','AD004'),
	   ('UA005','U004','AD005');

INSERT INTO Agents (Agent_ID, User_ID, Job_Title, Agency, Contact_Info) 
VALUES ('AG001','U001','Senior Agent','Star Realtors','3168565619'),
	   ('AG002','U002','Senior Agent','Moon Realtors','3268565629');

INSERT INTO Renters (Renter_ID, User_ID, Move_In_Date, Pref_Location, Budget) 
VALUES ('R001','U003','2025-12-01','Chicago','5000'),
	   ('R002','U004','2025-12-02','St. Louis','3200');

INSERT INTO Card (Card_ID, Renter_ID, Address_ID, Card_Number, Expiration) 
VALUES ('C001','R001','AD003','1234678221234123','05/28'),
	   ('C002','R002','AD004','1334678221234123','07/29'),
	   ('C003','R002','AD005','1434678221234123','06/26');

-------------------------------------Location Data-----------------------------------------------
INSERT INTO Locations (Location_ID, Address, City, State_, Country, Zip_Code) 
VALUES 
('L001','3303 S State St','Chicago','IL','United States','60616'),     -- Tim
('L002','3304 N State St','Chicago','IL','United States','60616'),     -- Aidan
('L003','12678 Honeygrove Ct','St. Louis','MO','United States','63146'), -- Yousef
('L004','12768 Honeygrove Ct','St. Louis','MO','United States','63146'), -- Emily
('L005','2301 S State St','Chicago','IL','United States','60616'),     -- Extra address for Emily
('L006','400 W Elm St','Chicago','IL','United States','60610'),		--Property Locations
('L007','410 W Oak St','Chicago','IL','United States','60611'),
('L008','12600 Honeygrove Ct','St. Louis','MO','United States','63146'),
('L009','500 N Lake Shore Dr','Chicago','IL','United States','60611'),
('L010','520 N Lake Shore Dr','Chicago','IL','United States','60611'),
('L011','700 Market St','St. Louis','MO','United States','63101'),
('L012','1200 Builders Way','Chicago','IL','United States','60605'),
('L013','1500 Vacation Ln','Orlando','FL','United States','32819');
	   
-------------------------------------Property Data-----------------------------------------------

INSERT INTO Property (Property_ID, Type_, Location_ID, Description, Price, Availability, Crime_Rate) 
VALUES ('P001','House','L006','A fun place to live','400000','1','0.001'),
	   ('P002','House','L007','A fun place to live','500000','1','0.0056'),
	   ('P003','House','L008','A fun place to live','1000000','1','0.002'),
	   ('P004','Apartment','L009','A fun place to rent','5000','1','0.001'),
	   ('P005','Apartment','L010','A fun place to rent','750','0','0.1'),
	   ('P006','Apartment','L004','A fun place to rent','1500','1','0.045'),
	   ('P007','Commercial Building','L011','A fun place to work','55000','1','0.0001'),
	   ('P008','Land','L012','A fun place to build','2000000','1','0.00001'),
	   ('P009','Vacation Home','L013','A fun place to relax','5000000','0','0.000001');

INSERT INTO Booking (Booking_ID, Card_ID, Property_ID, Renter_ID, Agent_ID, Start_Date, End_Date) 
VALUES ('B001','C002','P004','R002','AG001','2026-03-12','2027-03-15'),
	   ('B002','C003','P006','R002','AG001','2026-06-12','2027-06-11'),
	   ('B003','C001','P002','R001','AG002','2026-09-12','2027-09-10');

INSERT INTO House (House_ID, Property_ID, Num_Rooms, Sq_Footage) 
VALUES ('H001','P001','3','1900'),
	   ('H002','P002','4','2100'),
	   ('H003','P003','7','4000');

INSERT INTO Apartment (Apartment_ID, Property_ID, Num_Rooms, Sq_Footage, Building_Type) 
VALUES ('AP001','P004','2','750','Studio'),
	   ('AP002','P005','3','1500','Condo'),
	   ('AP003','P006','5','3000','Penthouse');

INSERT INTO Commercial_Buildings (Commercial_ID, Property_ID, Sq_Footage, Business_Type) 
VALUES ('CB001','P007','35000','Bank'),
	   ('CB002','P007','27000','Law Firm'),
	   ('CB003','P007','30000','Hardware Store');

INSERT INTO Land (Land_ID, Property_ID) 
VALUES ('LD001','P008'),
	   ('LD002','P008'),
	   ('LD003','P008');

INSERT INTO Vacation_Home (Vacation_ID, Property_ID) 
VALUES ('VH001','P009'),
	   ('VH002','P009'),
	   ('VH003','P009');
	   
INSERT INTO School (School_ID, Property_ID, School_Name, School_Address) 
VALUES ('S001','P001','Parkway North','106 S FeeFee Ln'),
	   ('S002','P002','Parkway South','66 N FeeFee Dr'),
	   ('S003','P003','Parkway East','56 S FeeFee Dr');

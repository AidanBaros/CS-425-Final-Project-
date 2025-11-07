------------------------------------- USERS & ADDRESSES -----------------------------------------------

INSERT INTO users (UserID, Name, Email, Type)
VALUES 
('u001','Tim','timEmail@email.com','Agent'),
('u002','Aidan','aidanEmail@email.com','Agent'),
('u003','Yousef','yousefEmail@email.com','Renter'),
('u004','Emily','emilyEmail@email.com','Renter');

INSERT INTO locations (LocationID, Address, City, State, ZipCode, Country)
VALUES 
-- User & Agent addresses
('l001','3303 S State St','Chicago','IL','60616','United States'),       -- Tim
('l002','3304 N State St','Chicago','IL','60616','United States'),       -- Aidan
('l003','12678 Honeygrove Ct','St. Louis','MO','63146','United States'), -- Yousef
('l004','12768 Honeygrove Ct','St. Louis','MO','63146','United States'), -- Emily
('l005','2301 S State St','Chicago','IL','60616','United States'),       -- Extra address for Emily

-- Property addresses
('l006','400 W Elm St','Chicago','IL','60610','United States'),
('l007','410 W Oak St','Chicago','IL','60611','United States'),
('l008','12600 Honeygrove Ct','St. Louis','MO','63146','United States'),
('l009','500 N Lake Shore Dr','Chicago','IL','60611','United States'),
('l010','520 N Lake Shore Dr','Chicago','IL','60611','United States'),
('l011','700 Market St','St. Louis','MO','63101','United States'),
('l012','1200 Builders Way','Chicago','IL','60605','United States'),
('l013','1500 Vacation Ln','Orlando','FL','32819','United States'),

-- School addresses
('l014','106 S FeeFee Ln','St. Louis','MO','63043','United States'),
('l015','66 N FeeFee Dr','St. Louis','MO','63043','United States'),
('l016','56 S FeeFee Dr','St. Louis','MO','63043','United States');

INSERT INTO user_x_address (UserAddressID, UserID, LocationID)
VALUES 
('ua001','u001','l001'),
('ua002','u002','l002'),
('ua003','u003','l003'),
('ua004','u004','l004'),
('ua005','u004','l005');

------------------------------------- AGENTS -----------------------------------------------

INSERT INTO agent (AgentID, UserID, JobTitle, Agency, ContactInfo)
VALUES
('ag001','u001','Senior Agent','Star Realtors','3168565619'),
('ag002','u002','Senior Agent','Moon Realtors','3268565629');

------------------------------------- RENTERS -----------------------------------------------

INSERT INTO renter (RenterID, UserID, MoveInDate, PreferedLocations, Budget)
VALUES
('r001','u003','2025-12-01','Chicago',5000.00),
('r002','u004','2025-12-02','St. Louis',3200.00);

------------------------------------- CARDS -----------------------------------------------

INSERT INTO card (CardID, RenterID, AddressID, CardNumber, ExpirationDate, CVV)
VALUES
('c001','r001','l003','1234678221234123','2028-05-01','123'),
('c002','r002','l004','1334678221234123','2029-07-01','456'),
('c003','r002','l005','1434678221234123','2026-06-01','789');

------------------------------------- PROPERTY -----------------------------------------------

INSERT INTO property (PropertyID, Type, LocationID, Description, Price, Availability, CrimeRate)
VALUES
('p001','House','l006','A fun place to live',400000.00,'Available','0.001'),
('p002','House','l007','A fun place to live',500000.00,'Available','0.0056'),
('p003','House','l008','A fun place to live',1000000.00,'Available','0.002'),
('p004','Apartment','l009','A fun place to rent',5000.00,'Available','0.001'),
('p005','Apartment','l010','A fun place to rent',750.00,'Unavailable','0.1'),
('p006','Apartment','l004','A fun place to rent',1500.00,'Available','0.045'),
('p007','Commercial Building','l011','A fun place to work',55000.00,'Available','0.0001'),
('p008','Land','l012','A fun place to build',2000000.00,'Available','0.00001'),
('p009','Vacation Home','l013','A fun place to relax',5000000.00,'Unavailable','0.000001');

------------------------------------- HOUSES -----------------------------------------------

INSERT INTO house (HouseID, PropertyID, NumRooms, SquareFeet)
VALUES
('h001','p001',3,1900),
('h002','p002',4,2100),
('h003','p003',7,4000);

------------------------------------- APARTMENTS -----------------------------------------------

INSERT INTO apartment (ApartmentID, PropertyID, BuildingType, Floor, NumRooms)
VALUES
('ap001','p004','Studio',1,2),
('ap002','p005','Condo',2,3),
('ap003','p006','Penthouse',5,5);

------------------------------------- COMMERCIAL BUILDINGS -----------------------------------------------

INSERT INTO commercialBuilding (CommercialBuildingID, PropertyID, SquareFeet, BusinessType)
VALUES
('cb001','p007',35000,'Bank'),
('cb002','p007',27000,'Law Firm'),
('cb003','p007',30000,'Hardware Store');

------------------------------------- LAND -----------------------------------------------

INSERT INTO land (LandID, PropertyID)
VALUES
('ld001','p008'),
('ld002','p008'),
('ld003','p008');

------------------------------------- VACATION HOMES -----------------------------------------------

INSERT INTO vacationHome (VacationHomeID, PropertyID)
VALUES
('vh001','p009'),
('vh002','p009'),
('vh003','p009');

------------------------------------- SCHOOLS -----------------------------------------------

INSERT INTO school (SchoolID, PropertyID, Name, AddressID)
VALUES
('s001','p001','Parkway North','l014'),
('s002','p002','Parkway South','l015'),
('s003','p003','Parkway East','l016');

------------------------------------- BOOKINGS -----------------------------------------------

INSERT INTO booking (BookingID, CardID, RenterID, AgentID, PropertyID, StartDate, EndDate)
VALUES
('b001','c002','r002','ag001','p004','2026-03-12','2027-03-15'),
('b002','c003','r002','ag001','p006','2026-06-12','2027-06-11'),
('b003','c001','r001','ag002','p002','2026-09-12','2027-09-10');

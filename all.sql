-- ===== Clean reset (safe re-run) =====
-- Drop in reverse dependency order so FKs don't block drops.
DROP TABLE IF EXISTS
    booking,
    school,
    vacationHome,
    land,
    house,
    commercialBuilding,
    apartment,
    card,
    user_x_address,
    agent,
    renter,
    property,
    locations,
    users
CASCADE;

-- ===== Create (dependency-safe order) =====

-- 1) users
CREATE TABLE users (
    UserID UUID PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Type VARCHAR(50) NOT NULL
);

-- 2) locations
CREATE TABLE locations (
    LocationID UUID PRIMARY KEY,
    Address VARCHAR(255) NOT NULL,
    City VARCHAR(100) NOT NULL,
    State VARCHAR(100) NOT NULL,
    ZipCode VARCHAR(20) NOT NULL,
    Country VARCHAR(100) NOT NULL
);

-- 3) property (depends on locations)
CREATE TABLE property (
    PropertyID UUID PRIMARY KEY,
    Type VARCHAR(50) NOT NULL,
    LocationID UUID REFERENCES locations (LocationID),
    Description TEXT NOT NULL,
    Price DECIMAL(10, 2) NOT NULL,
    Availability VARCHAR(50) NOT NULL,
    CrimeRate VARCHAR(50)
);

-- 4) renter (depends on users)
CREATE TABLE renter (
    RenterID UUID PRIMARY KEY,
    UserID UUID REFERENCES users (UserID),
    MoveInDate DATE NOT NULL,
    PreferredLocations VARCHAR(100),
    Budget DECIMAL(10, 2) NOT NULL
);

-- 5) agent (depends on users)
CREATE TABLE agent (
    AgentID UUID PRIMARY KEY,
    UserID UUID NOT NULL REFERENCES users (UserID),
    JobTitle VARCHAR(100),
    Agency VARCHAR(100),
    ContactInfo VARCHAR(255)
);

-- 6) user_x_address (depends on users, locations)
CREATE TABLE user_x_address (
    UserAddressID UUID PRIMARY KEY,
    UserID UUID REFERENCES users (UserID),
    LocationID UUID REFERENCES locations (LocationID)
);

-- 7) card (depends on renter, locations)
CREATE TABLE card (
    CardID UUID PRIMARY KEY,
    RenterID UUID REFERENCES renter (RenterID),
    AddressID UUID REFERENCES locations (LocationID),
    CardNumber VARCHAR(16) NOT NULL,
    ExpirationDate DATE NOT NULL,
    CVV VARCHAR(4) NOT NULL
);

-- 8) property subtypes (depend on property)
CREATE TABLE apartment (
    ApartmentID UUID PRIMARY KEY,
    PropertyID UUID REFERENCES property (PropertyID),
    BuildingType VARCHAR(20) NOT NULL,
    SquareFeet INT NOT NULL,
    NumRooms INT NOT NULL
);

CREATE TABLE commercialBuilding (
    CommercialBuildingID UUID PRIMARY KEY,
    PropertyID UUID REFERENCES property (PropertyID),
    SquareFeet INT NOT NULL,
    BusinessType VARCHAR(100) NOT NULL
);

CREATE TABLE house (
    HouseID UUID PRIMARY KEY,
    PropertyID UUID REFERENCES property (PropertyID),
    NumRooms INT NOT NULL,
    SquareFeet INT NOT NULL
);

CREATE TABLE land (
    LandID UUID PRIMARY KEY,
    PropertyID UUID REFERENCES property (PropertyID)
);

CREATE TABLE vacationHome (
    VacationHomeID UUID PRIMARY KEY,
    PropertyID UUID REFERENCES property (PropertyID)
);

CREATE TABLE school (
    SchoolID UUID PRIMARY KEY,
    PropertyID UUID REFERENCES property (PropertyID),
    Name VARCHAR(100) NOT NULL,
    AddressID UUID REFERENCES locations (LocationID)
);

-- 9) booking (depends on card, renter, agent, property)
CREATE TABLE booking (
    BookingID UUID PRIMARY KEY,
    CardID UUID REFERENCES card (CardID),
    RenterID UUID REFERENCES renter (RenterID),
    AgentID UUID REFERENCES agent (AgentID),
    PropertyID UUID NOT NULL REFERENCES property (PropertyID),
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL
);


-- ===== Sample Data ===== 


-- ------------------------------------- USERS & ADDRESSES -------------------------------------

INSERT INTO users (UserID, Name, Email, Type) VALUES
('00000000-0000-0000-0000-000000000001','Tim','timEmail@email.com','Agent'),
('00000000-0000-0000-0000-000000000002','Aidan','aidanEmail@email.com','Agent'),
('00000000-0000-0000-0000-000000000003','Yousef','yousefEmail@email.com','Renter'),
('00000000-0000-0000-0000-000000000004','Emily','emilyEmail@email.com','Renter');

INSERT INTO locations (LocationID, Address, City, State, ZipCode, Country) VALUES
-- User & Agent addresses
('00000000-0000-0000-0000-000000000101','3303 S State St','Chicago','IL','60616','United States'),       -- Tim
('00000000-0000-0000-0000-000000000102','3304 N State St','Chicago','IL','60616','United States'),       -- Aidan
('00000000-0000-0000-0000-000000000103','12678 Honeygrove Ct','St. Louis','MO','63146','United States'), -- Yousef
('00000000-0000-0000-0000-000000000104','12768 Honeygrove Ct','St. Louis','MO','63146','United States'), -- Emily
('00000000-0000-0000-0000-000000000105','2301 S State St','Chicago','IL','60616','United States'),       -- Extra address for Emily

-- Property addresses
('00000000-0000-0000-0000-000000000106','400 W Elm St','Chicago','IL','60610','United States'),
('00000000-0000-0000-0000-000000000107','410 W Oak St','Chicago','IL','60611','United States'),
('00000000-0000-0000-0000-000000000108','12600 Honeygrove Ct','St. Louis','MO','63146','United States'),
('00000000-0000-0000-0000-000000000109','500 N Lake Shore Dr','Chicago','IL','60611','United States'),
('00000000-0000-0000-0000-000000000110','520 N Lake Shore Dr','Chicago','IL','60611','United States'),
('00000000-0000-0000-0000-000000000111','700 Market St','St. Louis','MO','63101','United States'),
('00000000-0000-0000-0000-000000000112','1200 Builders Way','Chicago','IL','60605','United States'),
('00000000-0000-0000-0000-000000000113','1500 Vacation Ln','Orlando','FL','32819','United States'),

-- School addresses
('00000000-0000-0000-0000-000000000114','106 S FeeFee Ln','St. Louis','MO','63043','United States'),
('00000000-0000-0000-0000-000000000115','66 N FeeFee Dr','St. Louis','MO','63043','United States'),
('00000000-0000-0000-0000-000000000116','56 S FeeFee Dr','St. Louis','MO','63043','United States');

INSERT INTO user_x_address (UserAddressID, UserID, LocationID) VALUES
('00000000-0000-0000-0000-000000000201','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000101'),
('00000000-0000-0000-0000-000000000202','00000000-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000102'),
('00000000-0000-0000-0000-000000000203','00000000-0000-0000-0000-000000000003','00000000-0000-0000-0000-000000000103'),
('00000000-0000-0000-0000-000000000204','00000000-0000-0000-0000-000000000004','00000000-0000-0000-0000-000000000104'),
('00000000-0000-0000-0000-000000000205','00000000-0000-0000-0000-000000000004','00000000-0000-0000-0000-000000000105');

-- ------------------------------------- AGENTS -----------------------------------------------

INSERT INTO agent (AgentID, UserID, JobTitle, Agency, ContactInfo) VALUES
('00000000-0000-0000-0000-000000000301','00000000-0000-0000-0000-000000000001','Senior Agent','Star Realtors','3168565619'),
('00000000-0000-0000-0000-000000000302','00000000-0000-0000-0000-000000000002','Senior Agent','Moon Realtors','3268565629');

-- ------------------------------------- RENTERS -----------------------------------------------

INSERT INTO renter (RenterID, UserID, MoveInDate, PreferredLocations, Budget) VALUES
('00000000-0000-0000-0000-000000000401','00000000-0000-0000-0000-000000000003','2025-12-01','Chicago',5000.00),
('00000000-0000-0000-0000-000000000402','00000000-0000-0000-0000-000000000004','2025-12-02','St. Louis',3200.00);

-- ------------------------------------- CARDS -----------------------------------------------

INSERT INTO card (CardID, RenterID, AddressID, CardNumber, ExpirationDate, CVV) VALUES
('00000000-0000-0000-0000-000000000501','00000000-0000-0000-0000-000000000401','00000000-0000-0000-0000-000000000103','1234678221234123','2028-05-01','123'),
('00000000-0000-0000-0000-000000000502','00000000-0000-0000-0000-000000000402','00000000-0000-0000-0000-000000000104','1334678221234123','2029-07-01','456'),
('00000000-0000-0000-0000-000000000503','00000000-0000-0000-0000-000000000402','00000000-0000-0000-0000-000000000105','1434678221234123','2026-06-01','789');

-- ------------------------------------- PROPERTY -----------------------------------------------

INSERT INTO property (PropertyID, Type, LocationID, Description, Price, Availability, CrimeRate) VALUES
('00000000-0000-0000-0000-000000000601','House','00000000-0000-0000-0000-000000000106','A fun place to live',400000.00,'Available','0.001'),
('00000000-0000-0000-0000-000000000602','House','00000000-0000-0000-0000-000000000107','A fun place to live',500000.00,'Available','0.0056'),
('00000000-0000-0000-0000-000000000603','House','00000000-0000-0000-0000-000000000108','A fun place to live',1000000.00,'Available','0.002'),
('00000000-0000-0000-0000-000000000604','Apartment','00000000-0000-0000-0000-000000000109','A fun place to rent',5000.00,'Available','0.001'),
('00000000-0000-0000-0000-000000000605','Apartment','00000000-0000-0000-0000-000000000110','A fun place to rent',750.00,'Unavailable','0.1'),
('00000000-0000-0000-0000-000000000606','Apartment','00000000-0000-0000-0000-000000000104','A fun place to rent',1500.00,'Available','0.045'),
('00000000-0000-0000-0000-000000000607','Commercial Building','00000000-0000-0000-0000-000000000111','A fun place to work',55000.00,'Available','0.0001'),
('00000000-0000-0000-0000-000000000608','Land','00000000-0000-0000-0000-000000000112','A fun place to build',2000000.00,'Available','0.00001'),
('00000000-0000-0000-0000-000000000609','Vacation Home','00000000-0000-0000-0000-000000000113','A fun place to relax',5000000.00,'Unavailable','0.000001');

-- ------------------------------------- HOUSES -----------------------------------------------

INSERT INTO house (HouseID, PropertyID, NumRooms, SquareFeet) VALUES
('00000000-0000-0000-0000-000000000701','00000000-0000-0000-0000-000000000601',3,1900),
('00000000-0000-0000-0000-000000000702','00000000-0000-0000-0000-000000000602',4,2100),
('00000000-0000-0000-0000-000000000703','00000000-0000-0000-0000-000000000603',7,4000);

-- ------------------------------------- APARTMENTS -----------------------------------------------

INSERT INTO apartment (ApartmentID, PropertyID, BuildingType, SquareFeet, NumRooms) VALUES
('00000000-0000-0000-0000-000000000801','00000000-0000-0000-0000-000000000604','Studio',1000,2),
('00000000-0000-0000-0000-000000000802','00000000-0000-0000-0000-000000000605','Condo',2000,3),
('00000000-0000-0000-0000-000000000803','00000000-0000-0000-0000-000000000606','Penthouse',5000,5);

-- ------------------------------------- COMMERCIAL BUILDINGS -------------------------------------

INSERT INTO commercialBuilding (CommercialBuildingID, PropertyID, SquareFeet, BusinessType) VALUES
('00000000-0000-0000-0000-000000000901','00000000-0000-0000-0000-000000000607',35000,'Bank'),
('00000000-0000-0000-0000-000000000902','00000000-0000-0000-0000-000000000607',27000,'Law Firm'),
('00000000-0000-0000-0000-000000000903','00000000-0000-0000-0000-000000000607',30000,'Hardware Store');

-- ------------------------------------- LAND -----------------------------------------------

INSERT INTO land (LandID, PropertyID) VALUES
('00000000-0000-0000-0000-000000001001','00000000-0000-0000-0000-000000000608'),
('00000000-0000-0000-0000-000000001002','00000000-0000-0000-0000-000000000608'),
('00000000-0000-0000-0000-000000001003','00000000-0000-0000-0000-000000000608');

-- ------------------------------------- VACATION HOMES ----------------------------------------

INSERT INTO vacationHome (VacationHomeID, PropertyID) VALUES
('00000000-0000-0000-0000-000000001101','00000000-0000-0000-0000-000000000609'),
('00000000-0000-0000-0000-000000001102','00000000-0000-0000-0000-000000000609'),
('00000000-0000-0000-0000-000000001103','00000000-0000-0000-0000-000000000609');

-- ------------------------------------- SCHOOLS -----------------------------------------------

INSERT INTO school (SchoolID, PropertyID, Name, AddressID) VALUES
('00000000-0000-0000-0000-000000001201','00000000-0000-0000-0000-000000000601','Parkway North','00000000-0000-0000-0000-000000000114'),
('00000000-0000-0000-0000-000000001202','00000000-0000-0000-0000-000000000602','Parkway South','00000000-0000-0000-0000-000000000115'),
('00000000-0000-0000-0000-000000001203','00000000-0000-0000-0000-000000000603','Parkway East','00000000-0000-0000-0000-000000000116');

-- ------------------------------------- BOOKINGS -----------------------------------------------

INSERT INTO booking (BookingID, CardID, RenterID, AgentID, PropertyID, StartDate, EndDate) VALUES
('00000000-0000-0000-0000-000000001301','00000000-0000-0000-0000-000000000502','00000000-0000-0000-0000-000000000402','00000000-0000-0000-0000-000000000301','00000000-0000-0000-0000-000000000604','2026-03-12','2027-03-15'),
('00000000-0000-0000-0000-000000001302','00000000-0000-0000-0000-000000000503','00000000-0000-0000-0000-000000000402','00000000-0000-0000-0000-000000000301','00000000-0000-0000-0000-000000000606','2026-06-12','2027-06-11'),
('00000000-0000-0000-0000-000000001303','00000000-0000-0000-0000-000000000501','00000000-0000-0000-0000-000000000401','00000000-0000-0000-0000-000000000302','00000000-0000-0000-0000-000000000602','2026-09-12','2027-09-10');

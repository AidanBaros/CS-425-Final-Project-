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

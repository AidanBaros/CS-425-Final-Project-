DROP TABLE IF EXISTS booking;
DROP TABLE IF EXISTS card;
DROP TABLE IF EXISTS vacationHome;
DROP TABLE IF EXISTS land;
DROP TABLE IF EXISTS house;
DROP TABLE IF EXISTS apartment;
DROP TABLE IF EXISTS commercialBuilding;
DROP TABLE IF EXISTS school;
DROP TABLE IF EXISTS user_x_address;
DROP TABLE IF EXISTS renter;
DROP TABLE IF EXISTS agent;
DROP TABLE IF EXISTS property;
DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS users;

CREATE TABLE
    users (
        UserID VARCHAR(36) PRIMARY KEY,
        Name VARCHAR(100) NOT NULL,
        Email VARCHAR(100) UNIQUE NOT NULL,
        Type VARCHAR(50) NOT NULL
    );
CREATE TABLE
    locations (
        LocationID VARCHAR(36) PRIMARY KEY,
        Address VARCHAR(255) NOT NULL,
        City VARCHAR(100) NOT NULL,
        State VARCHAR(100) NOT NULL,
        ZipCode VARCHAR(20) NOT NULL,
        Country VARCHAR(100) NOT NULL
    );
CREATE TABLE
    property (
        PropertyID VARCHAR(36) PRIMARY KEY,
        Type VARCHAR(50) NOT NULL,
        LocationID VARCHAR(36) REFERENCES locations (LocationID),
        Description TEXT NOT NULL,
        Price DECIMAL(10, 2) NOT NULL,
        Availability VARCHAR(50) NOT NULL,
        CrimeRate VARCHAR(50)
    );

CREATE TABLE
    vacationHome (
        VacationHomeID VARCHAR(36) PRIMARY KEY,
        PropertyID VARCHAR(36) REFERENCES property (PropertyID)
    );
CREATE TABLE
    user_x_address (
        UserAddressID VARCHAR(36) PRIMARY KEY,
        UserID VARCHAR(36) REFERENCES users (UserID),
        LocationID VARCHAR(36) REFERENCES locations (LocationID)
    );

CREATE TABLE
    school (
        SchoolID VARCHAR(36) PRIMARY KEY,
        PropertyID VARCHAR(36) REFERENCES property (PropertyID),
        Name VARCHAR(100) NOT NULL,
        AddressID VARCHAR(36) REFERENCES locations (LocationID)
    );
CREATE TABLE
    renter (
        RenterID VARCHAR(36) PRIMARY KEY,
        UserID VARCHAR(36) REFERENCES users (UserID),
        MoveInDate DATE NOT NULL,
        PreferedLocations VARCHAR(100),
        Budget DECIMAL(10, 2) NOT NULL
    );


CREATE TABLE
    land (
        LandID VARCHAR(36) PRIMARY KEY,
        PropertyID VARCHAR(36) REFERENCES property (PropertyID)
    );
CREATE TABLE
    house (
        HouseID VARCHAR(36) PRIMARY KEY,
        PropertyID VARCHAR(36) REFERENCES property (PropertyID),
        NumRooms INT NOT NULL,
        SquareFeet INT NOT NULL
    );
CREATE TABLE
    commercialBuilding (
        CommercialBuildingID VARCHAR(36) PRIMARY KEY,
        PropertyID VARCHAR(36) REFERENCES property (PropertyID),
        SquareFeet INT NOT NULL,
        BusinessType VARCHAR(100) NOT NULL
    );
CREATE TABLE
    card (
        CardID VARCHAR(36) PRIMARY KEY,
        RenterID VARCHAR(36) REFERENCES renter (RenterID),
        AddressID VARCHAR(36) REFERENCES locations (LocationID),
        CardNumber VARCHAR(16) NOT NULL,
        ExpirationDate DATE NOT NULL,
        CVV VARCHAR(4) NOT NULL
    );
CREATE TABLE
    Agent (
        AgentID VARCHAR(36) PRIMARY KEY,
        UserID VARCHAR(36) NOT NULL,
        JobTitle VARCHAR(100),
        Agency VARCHAR(100),
        ContactInfo VARCHAR(255)
    );
CREATE TABLE
    booking (
        BookingID VARCHAR(36) PRIMARY KEY,
        CardID VARCHAR(36) REFERENCES card (CardID),
        RenterID VARCHAR(36) REFERENCES renter (RenterID),
        AgentID VARCHAR(36) REFERENCES agent (AgentID),
        PropertyID VARCHAR(36) NOT NULL,
        StartDate DATE NOT NULL,
        EndDate DATE NOT NULL
    );
CREATE TABLE
    apartment (
        ApartmentID VARCHAR(36) PRIMARY KEY,
        PropertyID VARCHAR(36) REFERENCES property (PropertyID),
        BuildingType VARCHAR(20) NOT NULL,
        Floor INT NOT NULL,
        NumRooms INT NOT NULL
    );
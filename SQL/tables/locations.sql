CREATE TABLE
    locations (
        LocationID UUID PRIMARY KEY,
        Address VARCHAR(255) NOT NULL,
        City VARCHAR(100) NOT NULL,
        State VARCHAR(100) NOT NULL,
        ZipCode VARCHAR(20) NOT NULL,
        Country VARCHAR(100) NOT NULL
    );
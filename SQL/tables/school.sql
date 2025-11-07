CREATE TABLE
    school (
        SchoolID UUID PRIMARY KEY,
        PropertyID UUID REFERENCES property (PropertyID),
        Name VARCHAR(100) NOT NULL,
        AddressID UUID REFERENCES locations (LocationID)
    );
CREATE TABLE
    property (
        PropertyID UUID PRIMARY KEY,
        Type VARCHAR(50) NOT NULL,
        LocationID UUID REFERENCES locations (LocationID),
        Description TEXT NOT NULL,
        Price DECIMAL(10, 2) NOT NULL,
        Availability VARCHAR(50) NOT NULL,
        CrimeRate VARCHAR(50)
    );
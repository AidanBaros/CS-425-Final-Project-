CREATE TABLE
    renter (
        RenterID UUID PRIMARY KEY,
        UserID UUID REFERENCES user (UserID),
        MoveInDate DATE NOT NULL,
        PreferedLocations VARCHAR(100),
        Budget DECIMAL(10, 2) NOT NULL
    );
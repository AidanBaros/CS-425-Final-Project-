CREATE TABLE
    house (
        HouseID UUID PRIMARY KEY,
        PropertyID UUID REFERENCES property (PropertyID),
        NumRooms INT NOT NULL,
        SquareFeet INT NOT NULL
    );
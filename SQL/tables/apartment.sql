CREATE TABLE
    apartment (
        ApartmentID UUID PRIMARY KEY,
        PropertyID UUID REFERENCES property (PropertyID),
        BuildingType VARCHAR(20) NOT NULL,
        Floor INT NOT NULL,
        NumRooms INT NOT NULL
    );
CREATE TABLE
    land (
        LandID UUID PRIMARY KEY,
        PropertyID UUID REFERENCES property (PropertyID)
    );
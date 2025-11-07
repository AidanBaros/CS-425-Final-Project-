CREATE TABLE
    commercialBuilding (
        CommercialBuildingID UUID PRIMARY KEY,
        PropertyID UUID REFERENCES property (PropertyID),
        SquareFeet INT NOT NULL,
        BusinessType VARCHAR(100) NOT NULL
    );
CREATE TABLE
    card (
        CardID UUID PRIMARY KEY,
        RenterID UUID REFERENCES renter (RenterID),
        AddressID UUID REFERENCES locations (LocationID),
        CardNumber VARCHAR(16) NOT NULL,
        ExpirationDate DATE NOT NULL,
        CVV VARCHAR(4) NOT NULL
    );
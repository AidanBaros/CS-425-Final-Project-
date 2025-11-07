CREATE TABLE
    booking (
        BookingID UUID PRIMARY KEY,
        CardID UUID REFERENCES card (CardID),
        RenterID UUID REFERENCES renter (RenterID),
        PropertyID UUID NOT NULL,
        StartDate DATE NOT NULL,
        EndDate DATE NOT NULL
    );
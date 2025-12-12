CREATE TABLE
    user_x_address (
        UserAddressID UUID PRIMARY KEY,
        UserID UUID REFERENCES user (UserID),
        LocationID UUID REFERENCES locations (LocationID)
    );
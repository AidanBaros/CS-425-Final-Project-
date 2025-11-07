CREATE TABLE
    user (
        UserID UUIST PRIMARY KEY,
        Name VARCHAR(100) NOT NULL,
        Email VARCHAR(100) UNIQUE NOT NULL,
        Type VARCHAR(50) NOT NULL
    );
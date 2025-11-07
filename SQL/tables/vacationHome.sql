CREATE TABLE
    vacationHome (
        VacationHomeID UUID PRIMARY KEY,
        PropertyID UUID REFERENCES property (PropertyID)
    );
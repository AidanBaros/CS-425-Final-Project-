CREATE TABLE
    Agent (
        AgentID UUID PRIMARY KEY,
        UserID UUID NOT NULL,
        JobTitle VARCHAR(100),
        Agency VARCHAR(100),
        ContactInfo VARCHAR(255)
    );
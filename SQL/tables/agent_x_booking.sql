CREATE TABLE
    agent_x_booking (
        AgentBookingID UUID PRIMARY KEY,
        AgentID UUID REFERENCES agent (AgentID),
        BookingID UUID REFERENCES booking (BookingID)
    );
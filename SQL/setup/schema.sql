\set ON_ERROR_STOP on

-- Optional: Drop and recreate the schema (comment out if you don't want that)
-- DROP SCHEMA IF EXISTS public CASCADE;
-- CREATE SCHEMA public;
-- SET search_path = public;

BEGIN;

\i SQL/tables/property.sql
\i SQL/tables/user.sql
\i SQL/tables/locations.sql
\i SQL/tables/agent.sql
\i SQL/tables/renter.sql
\i SQL/tables/school.sql
\i SQL/tables/house.sql
\i SQL/tables/apartment.sql
\i SQL/tables/commercialBuilding.sql
\i SQL/tables/land.sql
\i SQL/tables/vacationHome.sql
\i SQL/tables/card.sql
\i SQL/tables/user_x_address.sql
\i SQL/tables/booking.sql

COMMIT;

-- Optional: Verify schema creation
-- \dt

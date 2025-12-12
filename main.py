import psycopg2
import uuid
from datetime import datetime
import dotenv
import os   
import re

# main.py
# menu will be here with functions for each option
# will likely need multiple menus for different user types
# define functions for each option in the menu, we could make a seperate file for this too
# Functions:
# registration
# property search
# booking
# payment/address management
# agent property management
# booking management
# Global session state
current_user = None  # Dictionary with: {'user_id': str, 'name': str, 'email': str, 'type': str, 'renter_id': str or None, 'agent_id': str or None}
date_pattern = r"^\d{4}-\d{2}-\d{2}$"
dotenv.load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("dbname"),
    "user": os.getenv("user"),
    "password": os.getenv("password"),
    "host": os.getenv("host"),
    "port": os.getenv("port")
}

def get_connection():
    """ Connect to the PostgreSQL database server """
    try:
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(host=DB_CONFIG["host"], 
                                database=DB_CONFIG["dbname"],
                                user=DB_CONFIG["user"], 
                                password=DB_CONFIG["password"],
                                port=DB_CONFIG["port"])
        
        cur = conn.cursor()
        return conn, cur
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database connection error: {error}")
        return None, None

def login():
    """ Authenticate user by email and set session state """
    global current_user
    
    email = input("Enter your email: ").strip()
    if not email:
        print("Email cannot be empty.\n")
        return False
    
    conn, cur = get_connection()
    if conn is None:
        return False
    
    try:
        # query user by email
        cur.execute("SELECT UserID, Name, Email, Type FROM users WHERE Email = %s", (email,))
        user_row = cur.fetchone()
        
        if user_row is None:
            print("User not found. Please register first.\n")
            return False
        
        user_id, name, email, user_type = user_row
        current_user = {
            'user_id': str(user_id),
            'name': name,
            'email': email,
            'type': user_type
        }
        
        # if renter, get RenterID
        if user_type == 'Renter':
            cur.execute("SELECT RenterID FROM renter WHERE UserID = %s", (user_id,))
            renter_row = cur.fetchone()
            if renter_row:
                current_user['renter_id'] = str(renter_row[0])
        
        # if agent, get AgentID
        elif user_type == 'Agent':
            cur.execute("SELECT AgentID FROM agent WHERE UserID = %s", (user_id,))
            agent_row = cur.fetchone()
            if agent_row:
                current_user['agent_id'] = str(agent_row[0])
        
        print(f"\nWelcome, {name}! ({user_type})\n")
        return True
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Login error: {error}\n")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def logout():
    """ Clear current user session """
    global current_user
    if current_user:
        print(f"Goodbye, {current_user['name']}!\n")
    current_user = None

def register_account():
    """ Register a new account (Agent or Renter) """
    conn, cur = get_connection()
    if conn is None:
        return
    
    try:
        print("\n===== Account Registration =====")
        
        # get basic user information
        name = input("Enter your name: ").strip()
        if not name:
            print("Name cannot be empty.\n")
            return
        
        email = input("Enter your email: ").strip()
        if not email:
            print("Email cannot be empty.\n")
            return
        
        # check if email already exists
        cur.execute("SELECT UserID FROM users WHERE Email = %s", (email,))
        if cur.fetchone() is not None:
            print("Email already registered. Please use login instead.\n")
            return
        
        # get user type
        print("\nSelect user type:")
        print("1. Agent")
        print("2. Renter")
        type_choice = input("Enter choice (1 or 2): ").strip()
        
        if type_choice == "1":
            user_type = "Agent"
        elif type_choice == "2":
            user_type = "Renter"
        else:
            print("Invalid choice.\n")
            return
        
        # generate UserID
        user_id = str(uuid.uuid4())
        
        # insert into users table
        cur.execute("INSERT INTO users (UserID, Name, Email, Type) VALUES (%s, %s, %s, %s)",
                   (user_id, name, email, user_type))
        
        # if renter, get additional information
        if user_type == "Renter":
            move_in_date = input("Enter move-in date (YYYY-MM-DD): ").strip()
            if not move_in_date:
                print("Move-in date cannot be empty.\n")
                conn.rollback()
                return
            elif re.match(date_pattern, move_in_date):
                print("Not a valid date format. Use YYYY-MM-DD.\n")
            
            preferred_locations = input("Enter preferred locations (optional): ").strip()
            if not preferred_locations:
                preferred_locations = None
            
            budget_str = input("Enter budget: ").strip()
            try:
                budget = float(budget_str)
            except ValueError:
                print("Invalid budget amount.\n")
                conn.rollback()
                return
            
            renter_id = str(uuid.uuid4())
            cur.execute("INSERT INTO renter (RenterID, UserID, MoveInDate, PreferedLocations, Budget) VALUES (%s, %s, %s, %s, %s)",
                       (renter_id, user_id, move_in_date, preferred_locations, budget))
        
        # if agent, get additional information
        elif user_type == "Agent":
            job_title = input("Enter job title: ").strip()
            if not job_title:
                job_title = None
            
            agency = input("Enter agency name: ").strip()
            if not agency:
                agency = None
            
            contact_info = input("Enter contact information: ").strip()
            if not contact_info:
                contact_info = None
            
            agent_id = str(uuid.uuid4())
            cur.execute("INSERT INTO agent (AgentID, UserID, JobTitle, Agency, ContactInfo) VALUES (%s, %s, %s, %s, %s)",
                       (agent_id, user_id, job_title, agency, contact_info))
        
        # commit transaction
        conn.commit()
        print(f"\nRegistration successful! Hello, {name}!\n")
        print("Please login to continue.\n")
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Registration error: {error}\n")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def manage_payment_info():

    print("Functionality not implemented yet.\n")


def manage_addresses():

    print("Functionality not implemented yet.\n")

def manage_properties():
    """Agent: Add / Delete / Modify properties."""
    global current_user

    if current_user is None or current_user.get("type") != "Agent":
        print("You must be logged in as an Agent to manage properties.\n")
        return

    while True:
        print("\n===== Manage Properties (Agent) =====")
        print("1. List All Properties")
        print("2. Add New Property")
        print("3. Modify Existing Property")
        print("4. Delete Property")
        print("0. Back to Agent Menu")

        choice = input("Select an option: ").strip()

        if choice == "1":
            list_all_properties()
        elif choice == "2":
            add_property()
        elif choice == "3":
            modify_property()
        elif choice == "4":
            delete_property()
        elif choice == "0":
            break
        else:
            print("Invalid option.\n")


def list_all_properties():
    """List all properties with basic info."""
    conn, cur = get_connection()
    if conn is None:
        return

    try:
        cur.execute("""
            SELECT p.propertyid, p.type, p.description, p.price, p.availability, p.crimerate,
                   l.address, l.city, l.state, l.zipcode, l.country
            FROM property p
            JOIN locations l ON p.locationid = l.locationid
            ORDER BY l.city, l.state, p.price;
        """)
        rows = cur.fetchall()

        if not rows:
            print("\nThere are no properties in the system.\n")
            return

        print("\n===== All Properties =====")
        for row in rows:
            (pid, ptype, desc, price, avail, crime,
             addr, city, state, zipcode, country) = row
            print(f"Property ID: {pid}")
            print(f"  Type: {ptype}")
            print(f"  Address: {addr}, {city}, {state} {zipcode}, {country}")
            print(f"  Price: ${price:.2f}")
            print(f"  Availability: {avail}")
            print(f"  Crime Rate: {crime}")
            print("-" * 40)

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error listing properties: {error}\n")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def add_property():
    """Add a new property and its specific subtype row."""
    conn, cur = get_connection()
    if conn is None:
        return

    try:
        print("\n===== Add New Property =====")
        # Address / location info
        address = input("Street address: ").strip()
        city = input("City: ").strip()
        state = input("State: ").strip()
        zipcode = input("Zip code: ").strip()
        country = input("Country: ").strip()

        if not (address and city and state and zipcode and country):
            print("All address fields are required.\n")
            return

        # Property core info
        print("\nProperty type options:")
        print("1. House")
        print("2. Apartment")
        print("3. CommercialBuilding")
        print("4. Land")
        print("5. VacationHome")
        type_choice = input("Select property type (1-5): ").strip()

        type_map = {
            "1": "House",
            "2": "Apartment",
            "3": "CommercialBuilding",
            "4": "Land",
            "5": "VacationHome"
        }
        if type_choice not in type_map:
            print("Invalid property type choice.\n")
            return
        ptype = type_map[type_choice]

        description = input("Description: ").strip()
        if not description:
            print("Description cannot be empty.\n")
            return

        price_str = input("Price (e.g., 1200.00): ").strip()
        try:
            price = float(price_str)
        except ValueError:
            print("Invalid price.\n")
            return

        availability = input("Availability (e.g., 'Available', 'Not Available', 'For Rent'): ").strip()
        if not availability:
            print("Availability cannot be empty.\n")
            return

        crime_rate = input("Crime rate description (optional): ").strip()
        if not crime_rate:
            crime_rate = None

        # Insert location
        location_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO locations (locationid, address, city, state, zipcode, country)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (location_id, address, city, state, zipcode, country))

        # Insert property
        property_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO property (propertyid, type, locationid, description, price, availability, crimerate)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (property_id, ptype, location_id, description, price, availability, crime_rate))

        # Insert into subtype table based on type
        if ptype == "House":
            num_rooms_str = input("Number of rooms: ").strip()
            sqft_str = input("Square feet: ").strip()
            try:
                num_rooms = int(num_rooms_str)
                sqft = int(sqft_str)
            except ValueError:
                print("Invalid rooms or square feet.\n")
                conn.rollback()
                return
            house_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO house (houseid, propertyid, numrooms, squarefeet)
                VALUES (%s, %s, %s, %s);
            """, (house_id, property_id, num_rooms, sqft))

        elif ptype == "Apartment":
            building_type = input("Building type (e.g., 'HighRise'): ").strip()
            floor_str = input("Floor: ").strip()
            num_rooms_str = input("Number of rooms: ").strip()
            try:
                floor = int(floor_str)
                num_rooms = int(num_rooms_str)
            except ValueError:
                print("Invalid floor or number of rooms.\n")
                conn.rollback()
                return
            apt_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO apartment (apartmentid, propertyid, buildingtype, floor, numrooms)
                VALUES (%s, %s, %s, %s, %s);
            """, (apt_id, property_id, building_type, floor, num_rooms))

        elif ptype == "CommercialBuilding":
            sqft_str = input("Square feet: ").strip()
            business_type = input("Type of business allowed (e.g., 'Retail'): ").strip()
            try:
                sqft = int(sqft_str)
            except ValueError:
                print("Invalid square feet.\n")
                conn.rollback()
                return
            cb_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO commercialbuilding (commercialbuildingid, propertyid, squarefeet, businesstype)
                VALUES (%s, %s, %s, %s);
            """, (cb_id, property_id, sqft, business_type))

        elif ptype == "Land":
            land_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO land (landid, propertyid)
                VALUES (%s, %s);
            """, (land_id, property_id))

        elif ptype == "VacationHome":
            vh_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO vacationhome (vacationhomeid, propertyid)
                VALUES (%s, %s);
            """, (vh_id, property_id))

        conn.commit()
        print("\nProperty added successfully!\n")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error adding property: {error}\n")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def modify_property():
    """Modify basic property and location information."""
    conn, cur = get_connection()
    if conn is None:
        return

    try:
        list_all_properties()
        pid = input("\nEnter Property ID to modify (or blank to cancel): ").strip()
        if not pid:
            return

        # Load existing data
        cur.execute("""
            SELECT p.propertyid, p.type, p.description, p.price, p.availability, p.crimerate,
                   l.locationid, l.address, l.city, l.state, l.zipcode, l.country
            FROM property p
            JOIN locations l ON p.locationid = l.locationid
            WHERE p.propertyid = %s;
        """, (pid,))
        row = cur.fetchone()

        if not row:
            print("No such property.\n")
            return

        (propertyid, ptype, desc, price, avail, crime,
         locid, address, city, state, zipcode, country) = row

        print("\nLeave any field blank to keep current value.")

        new_desc = input(f"Description [{desc}]: ").strip() or desc

        price_str = input(f"Price [{price}]: ").strip()
        if price_str:
            try:
                new_price = float(price_str)
            except ValueError:
                print("Invalid price; keeping old value.")
                new_price = price
        else:
            new_price = price

        new_avail = input(f"Availability [{avail}]: ").strip() or avail
        new_crime = input(f"Crime rate [{crime}]: ").strip() or crime

        new_address = input(f"Address [{address}]: ").strip() or address
        new_city = input(f"City [{city}]: ").strip() or city
        new_state = input(f"State [{state}]: ").strip() or state
        new_zip = input(f"Zip code [{zipcode}]: ").strip() or zipcode
        new_country = input(f"Country [{country}]: ").strip() or country

        # Update property
        cur.execute("""
            UPDATE property
            SET description = %s, price = %s, availability = %s, crimerate = %s
            WHERE propertyid = %s;
        """, (new_desc, new_price, new_avail, new_crime, propertyid))

        # Update location
        cur.execute("""
            UPDATE locations
            SET address = %s, city = %s, state = %s, zipcode = %s, country = %s
            WHERE locationid = %s;
        """, (new_address, new_city, new_state, new_zip, new_country, locid))

        conn.commit()
        print("\nProperty updated successfully!\n")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error modifying property: {error}\n")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def delete_property():
    """Delete a property (if there are no bookings)."""
    conn, cur = get_connection()
    if conn is None:
        return

    try:
        list_all_properties()
        pid = input("\nEnter Property ID to delete (or blank to cancel): ").strip()
        if not pid:
            return

        # Check for existing bookings
        cur.execute("""
            SELECT COUNT(*) FROM booking WHERE propertyid = %s;
        """, (pid,))
        count = cur.fetchone()[0]
        if count > 0:
            print("Cannot delete property with existing bookings.\n")
            return

        # Find type and location for cleanup
        cur.execute("""
            SELECT type, locationid
            FROM property
            WHERE propertyid = %s;
        """, (pid,))
        row = cur.fetchone()
        if not row:
            print("No such property.\n")
            return

        ptype, locid = row

        # Delete subtype row first
        if ptype == "House":
            cur.execute("DELETE FROM house WHERE propertyid = %s;", (pid,))
        elif ptype == "Apartment":
            cur.execute("DELETE FROM apartment WHERE propertyid = %s;", (pid,))
        elif ptype == "CommercialBuilding":
            cur.execute("DELETE FROM commercialbuilding WHERE propertyid = %s;", (pid,))
        elif ptype == "Land":
            cur.execute("DELETE FROM land WHERE propertyid = %s;", (pid,))
        elif ptype == "VacationHome":
            cur.execute("DELETE FROM vacationhome WHERE propertyid = %s;", (pid,))

        # Delete property
        cur.execute("DELETE FROM property WHERE propertyid = %s;", (pid,))

        # NOTE: We leave the location row in case other entities reference it (schools, cards, etc.)

        conn.commit()
        print("Property deleted successfully.\n")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error deleting property: {error}\n")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def search_properties():

    print("Functionality not implemented yet.\n")

def book_property():

    print("Functionality not implemented yet.\n")

def manage_bookings():
    """View / cancel bookings.

    - Renters: their own bookings.
    - Agents: bookings for properties under their agency.
    """
    global current_user

    if current_user is None:
        print("You must be logged in to manage bookings.\n")
        return

    user_type = current_user.get("type")

    if user_type == "Renter":
        manage_renter_bookings()
    elif user_type == "Agent":
        manage_agent_bookings()
    else:
        print("Unknown user type.\n")


def manage_renter_bookings():
    
    print("Functionality not implemented yet.\n")


def manage_agent_bookings():
    """Agent: view and cancel bookings for properties under their agency."""
    agent_id = current_user.get("agent_id")
    if not agent_id:
        print("Agent ID not found for current user.\n")
        return

    conn, cur = get_connection()
    if conn is None:
        return

    try:
        while True:
            print("\n===== Bookings for My Agency =====")

            cur.execute("""
                SELECT b.bookingid,
                       p.propertyid, p.type, p.description, p.price,
                       l.address, l.city, l.state, l.zipcode,
                       b.startdate, b.enddate,
                       u.name AS renter_name, u.email AS renter_email,
                       c.cardnumber
                FROM booking b
                JOIN property p ON b.propertyid = p.propertyid
                JOIN locations l ON p.locationid = l.locationid
                JOIN renter r ON b.renterid = r.renterid
                JOIN users u ON r.userid = u.userid
                JOIN card c ON b.cardid = c.cardid
                WHERE b.agentid = %s
                ORDER BY b.startdate DESC;
            """, (agent_id,))
            rows = cur.fetchall()

            if not rows:
                print("There are no bookings associated with your agency.\n")
            else:
                for row in rows:
                    (bookingid, pid, ptype, desc, price,
                     addr, city, state, zipcode,
                     startdate, enddate,
                     renter_name, renter_email,
                     cardnumber) = row
                    masked_card = "**** **** **** " + cardnumber[-4:]
                    print(f"Booking ID: {bookingid}")
                    print(f"  Property: {ptype} ({pid})")
                    print(f"  Address: {addr}, {city}, {state} {zipcode}")
                    print(f"  Description: {desc}")
                    print(f"  Price (per period unit): ${price:.2f}")
                    print(f"  Rental Period: {startdate} to {enddate}")
                    print(f"  Renter: {renter_name} <{renter_email}>")
                    print(f"  Payment Method: {masked_card}")
                    print("-" * 40)

            print("1. Cancel a booking")
            print("0. Back")
            choice = input("Select an option: ").strip()

            if choice == "1":
                bid = input("Enter Booking ID to cancel (or blank to cancel): ").strip()
                if not bid:
                    continue

                # Ensure booking belongs to this agent (via booking.agentid)
                cur.execute("""
                    DELETE FROM booking
                    WHERE bookingid = %s AND agentid = %s;
                """, (bid, agent_id))
                if cur.rowcount == 0:
                    print("No such booking found for your agency.\n")
                else:
                    conn.commit()
                    print("Booking cancelled.\n")
            elif choice == "0":
                break
            else:
                print("Invalid option.\n")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error managing agent bookings: {error}\n")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def renter_menu():
    """ Menu for logged-in renters """
    while True:
        print("\n===== Renter Menu =====")
        print("1. Manage Payment Information")
        print("2. Manage Addresses")
        print("3. Search Properties")
        print("4. Book a Property")
        print("5. View/Cancel My Bookings")
        print("6. Logout")
        print("0. Exit Program")

        choice = input("Select an option: ").strip()

        if choice == "1":
            manage_payment_info()
        elif choice == "2":
            manage_addresses()
        elif choice == "3":
            search_properties()
        elif choice == "4":
            book_property()
        elif choice == "5":
            manage_bookings()
        elif choice == "6":
            logout()
            break
        elif choice == "0":
            print("Exiting program.")
            exit(0)
        else:
            print("Invalid option.\n")

def agent_menu():
    """ Menu for logged-in agents """
    while True:
        print("\n===== Agent Menu =====")
        print("1. Add/Delete/Modify Properties")
        print("2. Search Properties")
        print("3. View/Cancel Bookings (My Properties)")
        print("4. Logout")
        print("0. Exit Program")

        choice = input("Select an option: ").strip()

        if choice == "1":
            manage_properties()
        elif choice == "2":
            search_properties()
        elif choice == "3":
            manage_bookings()
        elif choice == "4":
            logout()
            break
        elif choice == "0":
            print("Exiting program.")
            exit(0)
        else:
            print("Invalid option.\n")

def main_menu():
    # first user login, then we continue to user menu depending on user type
    global current_user
    while True:
        print("\n===== Real Estate Booking System =====")
        
        if current_user is None:
            # not logged in
            print("1. Register Account")
            print("2. Login")
            print("0. Exit")
            
            choice = input("Select an option: ").strip()
            
            if choice == "1":
                register_account()
            elif choice == "2":
                if login():
                    # route to appropriate menu based on user type
                    if current_user['type'] == 'Renter':
                        renter_menu()
                    elif current_user['type'] == 'Agent':
                        agent_menu()
            elif choice == "0":
                print("Exiting program.")
                break
            else:
                print("Invalid option.\n")
        else:
            print("Already logged in. Use logout from your menu.")
            break

if __name__ == "__main__":
    main_menu()
import psycopg2
import uuid
from datetime import datetime
import dotenv
import os
import re

# main.py
# Functions:
# - registration
# - property search
# - booking
# - payment/address management
# - agent property management
# - booking management

# Global session state
current_user = None  # {'user_id', 'name', 'email', 'type', 'renter_id'?, 'agent_id'?}
date_pattern = r"^\d{4}-\d{2}-\d{2}$"

dotenv.load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("dbname"),
    "user": os.getenv("user"),
    "password": os.getenv("password"),
    "host": os.getenv("host"),
    "port": os.getenv("port"),
}

def read_date(prompt: str):
    s = input(prompt).strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date. Use YYYY-MM-DD.\n")
        return None


def get_connection():
    """Connect to the PostgreSQL database server using .env config."""
    try:
        print("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            database=DB_CONFIG["dbname"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=DB_CONFIG["port"],
        )
        cur = conn.cursor()
        return conn, cur
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database connection error: {error}")
        return None, None


def login():
    """Authenticate user by email and set session state."""
    global current_user

    email = input("Enter your email: ").strip()
    if not email:
        print("Email cannot be empty.\n")
        return False

    conn, cur = get_connection()
    if conn is None:
        return False

    try:
        cur.execute(
            "SELECT UserID, Name, Email, Type FROM users WHERE Email = %s", (email,)
        )
        user_row = cur.fetchone()

        if user_row is None:
            print("User not found. Please register first.\n")
            return False

        user_id, name, email, user_type = user_row
        current_user = {
            "user_id": str(user_id),
            "name": name,
            "email": email,
            "type": user_type,
        }

        if user_type == "Renter":
            cur.execute("SELECT RenterID FROM renter WHERE UserID = %s", (user_id,))
            renter_row = cur.fetchone()
            if renter_row:
                current_user["renter_id"] = str(renter_row[0])

        elif user_type == "Agent":
            cur.execute("SELECT AgentID FROM agent WHERE UserID = %s", (user_id,))
            agent_row = cur.fetchone()
            if agent_row:
                current_user["agent_id"] = str(agent_row[0])

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
    """Clear current user session."""
    global current_user
    if current_user:
        print(f"Goodbye, {current_user['name']}!\n")
    current_user = None


def register_account():
    """Register a new account (Agent or Renter)."""
    conn, cur = get_connection()
    if conn is None:
        return

    try:
        print("\n===== Account Registration =====")

        name = input("Enter your name: ").strip()
        if not name:
            print("Name cannot be empty.\n")
            return

        email = input("Enter your email: ").strip()
        if not email:
            print("Email cannot be empty.\n")
            return

        cur.execute("SELECT UserID FROM users WHERE Email = %s", (email,))
        if cur.fetchone() is not None:
            print("Email already registered. Please use login instead.\n")
            return

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

        user_id = str(uuid.uuid4())

        cur.execute(
            "INSERT INTO users (UserID, Name, Email, Type) VALUES (%s, %s, %s, %s)",
            (user_id, name, email, user_type),
        )

        if user_type == "Renter":
            move_in_date = read_date("Enter move-in date (YYYY-MM-DD): ")
            if move_in_date is None:
                print("Move-in date cannot be empty or invalid.\n")
                conn.rollback()
                return

            preferred_locations = input(
                "Enter preferred locations (optional): "
            ).strip()
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
            cur.execute(
                "INSERT INTO renter (RenterID, UserID, MoveInDate, PreferedLocations, Budget) "
                "VALUES (%s, %s, %s, %s, %s)",
                (renter_id, user_id, move_in_date, preferred_locations, budget),
            )

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
            cur.execute(
                "INSERT INTO agent (AgentID, UserID, JobTitle, Agency, ContactInfo) "
                "VALUES (%s, %s, %s, %s, %s)",
                (agent_id, user_id, job_title, agency, contact_info),
            )

        conn.commit()
        print(f"\nRegistration successful! Hello, {name}!\n")
        print("Please login to continue.\n")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Registration error: {error}\n")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


# ===================== RENTER: PAYMENT INFO =====================

def renter_manage_payment_info():
    global current_user
    if current_user is None or current_user.get("type") != "Renter":
        print("You must be logged in as a renter to manage payment information.\n")
        return

    renter_id = current_user.get("renter_id")

    if renter_id is None:
        conn, cur = get_connection()
        if conn is None:
            return
        try:
            cur.execute(
                "SELECT RenterID FROM renter WHERE UserID = %s",
                (current_user["user_id"],),
            )
            row = cur.fetchone()
            if row is None:
                print("No renter record found for current user.\n")
                return
            renter_id = str(row[0])
            current_user["renter_id"] = renter_id
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error loading renter info: {error}\n")
            conn.rollback()
            return
        finally:
            cur.close()
            conn.close()

    while True:
        print("\n===== Payment Information =====")
        print("1. Add Credit Card")
        print("2. Modify Credit Card")
        print("3. Delete Credit Card")
        print("4. View My Cards")
        print("0. Back")

        choice = input("Select an option: ").strip()

        if choice == "0":
            break

        conn, cur = get_connection()
        if conn is None:
            return

        try:
            if choice == "4":
                cur.execute(
                    "SELECT CardID, CardNumber, ExpirationDate, CVV, AddressID "
                    "FROM card WHERE RenterID = %s",
                    (renter_id,),
                )
                rows = cur.fetchall()
                if not rows:
                    print("No cards found.\n")
                else:
                    print("\nYour cards:")
                    for idx, (card_id, number, exp, cvv, addr_id) in enumerate(
                        rows, start=1
                    ):
                        num_str = str(number)
                        if len(num_str) > 4:
                            masked = "*" * (len(num_str) - 4) + num_str[-4:]
                        else:
                            masked = num_str
                        print(
                            f"{idx}. CardID {card_id}, Number {masked}, Exp {exp}, AddressID {addr_id}"
                        )
                    print()

            elif choice == "1":
                cur.execute(
                    "SELECT l.LocationID, l.Address, l.City, l.State, l.ZipCode, l.Country "
                    "FROM user_x_address ua JOIN locations l ON ua.LocationID = l.LocationID "
                    "WHERE ua.UserID = %s",
                    (current_user["user_id"],),
                )
                addresses = cur.fetchall()
                if not addresses:
                    print("You must add an address before adding a card.\n")
                else:
                    print("\nSelect billing address:")
                    for idx, row in enumerate(addresses, start=1):
                        loc_id, addr, city, state, zipcode, country = row
                        print(
                            f"{idx}. {addr}, {city}, {state} {zipcode}, {country} (LocationID {loc_id})"
                        )
                    addr_choice = input(
                        "Enter number of billing address: "
                    ).strip()
                    try:
                        addr_idx = int(addr_choice)
                        if addr_idx < 1 or addr_idx > len(addresses):
                            print("Invalid selection.\n")
                        else:
                            location_id = addresses[addr_idx - 1][0]
                            card_number = input("Enter card number: ").strip()
                            expiration_date = input(
                                "Enter expiration date (YYYY-MM-DD): "
                            ).strip()
                            cvv = input("Enter CVV: ").strip()
                            card_id = str(uuid.uuid4())
                            cur.execute(
                                "INSERT INTO card (CardID, RenterID, AddressID, CardNumber, ExpirationDate, CVV) "
                                "VALUES (%s, %s, %s, %s, %s, %s)",
                                (
                                    card_id,
                                    renter_id,
                                    location_id,
                                    card_number,
                                    expiration_date,
                                    cvv,
                                ),
                            )
                            conn.commit()
                            print("Card added.\n")
                    except ValueError:
                        print("Invalid selection.\n")

            elif choice == "2":
                cur.execute(
                    "SELECT CardID, CardNumber, ExpirationDate, CVV, AddressID "
                    "FROM card WHERE RenterID = %s",
                    (renter_id,),
                )
                cards = cur.fetchall()
                if not cards:
                    print("No cards to modify.\n")
                else:
                    print("\nSelect card to modify:")
                    for idx, row in enumerate(cards, start=1):
                        card_id, number, exp, cvv, addr_id = row
                        num_str = str(number)
                        if len(num_str) > 4:
                            masked = "*" * (len(num_str) - 4) + num_str[-4:]
                        else:
                            masked = num_str
                        print(
                            f"{idx}. CardID {card_id}, Number {masked}, Exp {exp}"
                        )
                    card_choice = input("Enter number of card: ").strip()
                    try:
                        card_idx = int(card_choice)
                        if card_idx < 1 or card_idx > len(cards):
                            print("Invalid selection.\n")
                        else:
                            card_id, number, exp, cvv, addr_id = cards[card_idx - 1]
                            new_number = input(
                                "Enter new card number (leave blank to keep current): "
                            ).strip()
                            new_exp = input(
                                "Enter new expiration date YYYY-MM-DD (leave blank to keep current): "
                            ).strip()
                            new_cvv = input(
                                "Enter new CVV (leave blank to keep current): "
                            ).strip()
                            if not new_number:
                                new_number = number
                            if not new_exp:
                                new_exp = exp
                            if not new_cvv:
                                new_cvv = cvv
                            cur.execute(
                                "UPDATE card SET CardNumber = %s, ExpirationDate = %s, CVV = %s "
                                "WHERE CardID = %s AND RenterID = %s",
                                (new_number, new_exp, new_cvv, card_id, renter_id),
                            )
                            conn.commit()
                            print("Card updated.\n")
                    except ValueError:
                        print("Invalid selection.\n")

            elif choice == "3":
                cur.execute(
                    "SELECT CardID, CardNumber, ExpirationDate, CVV, AddressID "
                    "FROM card WHERE RenterID = %s",
                    (renter_id,),
                )
                cards = cur.fetchall()
                if not cards:
                    print("No cards to delete.\n")
                else:
                    print("\nSelect card to delete:")
                    for idx, row in enumerate(cards, start=1):
                        card_id, number, exp, cvv, addr_id = row
                        num_str = str(number)
                        if len(num_str) > 4:
                            masked = "*" * (len(num_str) - 4) + num_str[-4:]
                        else:
                            masked = num_str
                        print(
                            f"{idx}. CardID {card_id}, Number {masked}, Exp {exp}"
                        )
                    card_choice = input("Enter number of card: ").strip()
                    try:
                        card_idx = int(card_choice)
                        if card_idx < 1 or card_idx > len(cards):
                            print("Invalid selection.\n")
                        else:
                            card_id, number, exp, cvv, addr_id = cards[card_idx - 1]
                            cur.execute(
                                "SELECT COUNT(*) FROM booking WHERE CardID = %s AND EndDate >= CURRENT_DATE",
                                (card_id,),
                            )
                            count = cur.fetchone()[0]
                            if count > 0:
                                print(
                                    "Cannot delete card with active bookings.\n"
                                )
                            else:
                                cur.execute(
                                    "DELETE FROM card WHERE CardID = %s AND RenterID = %s",
                                    (card_id, renter_id),
                                )
                                conn.commit()
                                print("Card deleted.\n")
                    except ValueError:
                        print("Invalid selection.\n")

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Payment error: {error}\n")
            conn.rollback()
        finally:
            cur.close()
            conn.close()


# ===================== RENTER: ADDRESSES =====================

def renter_manage_addresses():
    global current_user
    if current_user is None or current_user.get("type") != "Renter":
        print("You must be logged in as a renter to manage addresses.\n")
        return

    user_id = current_user["user_id"]

    while True:
        print("\n===== Address Management =====")
        print("1. Add Address")
        print("2. Modify Address")
        print("3. Delete Address")
        print("4. View My Addresses")
        print("0. Back")

        choice = input("Select an option: ").strip()

        if choice == "0":
            break

        conn, cur = get_connection()
        if conn is None:
            return

        try:
            if choice == "4":
                cur.execute(
                    "SELECT l.LocationID, l.Address, l.City, l.State, l.ZipCode, l.Country "
                    "FROM user_x_address ua JOIN locations l ON ua.LocationID = l.LocationID "
                    "WHERE ua.UserID = %s",
                    (user_id,),
                )
                rows = cur.fetchall()
                if not rows:
                    print("No addresses found.\n")
                else:
                    print("\nYour addresses:")
                    for idx, (loc_id, addr, city, state, zipcode, country) in enumerate(
                        rows, start=1
                    ):
                        print(
                            f"{idx}. {addr}, {city}, {state} {zipcode}, {country} (LocationID {loc_id})"
                        )
                    print()

            elif choice == "1":
                location_id = str(uuid.uuid4())
                address = input("Enter street address: ").strip()
                city = input("Enter city: ").strip()
                state = input("Enter state: ").strip()
                zipcode = input("Enter zip code: ").strip()
                country = input("Enter country: ").strip()

                if not address or not city or not state or not zipcode or not country:
                    print("All address fields are required.\n")
                else:
                    cur.execute(
                        "INSERT INTO locations (LocationID, Address, City, State, ZipCode, Country) "
                        "VALUES (%s, %s, %s, %s, %s, %s)",
                        (location_id, address, city, state, zipcode, country),
                    )
                    user_address_id = str(uuid.uuid4())
                    cur.execute(
                        "INSERT INTO user_x_address (UserAddressID, UserID, LocationID) "
                        "VALUES (%s, %s, %s)",
                        (user_address_id, user_id, location_id),
                    )
                    conn.commit()
                    print("Address added.\n")

            elif choice == "2":
                cur.execute(
                    "SELECT l.LocationID, l.Address, l.City, l.State, l.ZipCode, l.Country "
                    "FROM user_x_address ua JOIN locations l ON ua.LocationID = l.LocationID "
                    "WHERE ua.UserID = %s",
                    (user_id,),
                )
                rows = cur.fetchall()
                if not rows:
                    print("No addresses to modify.\n")
                else:
                    print("\nSelect address to modify:")
                    for idx, (loc_id, addr, city, state, zipcode, country) in enumerate(
                        rows, start=1
                    ):
                        print(
                            f"{idx}. {addr}, {city}, {state} {zipcode}, {country} (LocationID {loc_id})"
                        )
                    choice_idx = input("Enter number of address: ").strip()
                    try:
                        addr_idx = int(choice_idx)
                        if addr_idx < 1 or addr_idx > len(rows):
                            print("Invalid selection.\n")
                        else:
                            loc_id, addr, city, state, zipcode, country = rows[
                                addr_idx - 1
                            ]
                            new_address = input(
                                "Enter new street address (leave blank to keep current): "
                            ).strip()
                            new_city = input(
                                "Enter new city (leave blank to keep current): "
                            ).strip()
                            new_state = input(
                                "Enter new state (leave blank to keep current): "
                            ).strip()
                            new_zipcode = input(
                                "Enter new zip code (leave blank to keep current): "
                            ).strip()
                            new_country = input(
                                "Enter new country (leave blank to keep current): "
                            ).strip()
                            if not new_address:
                                new_address = addr
                            if not new_city:
                                new_city = city
                            if not new_state:
                                new_state = state
                            if not new_zipcode:
                                new_zipcode = zipcode
                            if not new_country:
                                new_country = country
                            cur.execute(
                                "UPDATE locations SET Address = %s, City = %s, State = %s, ZipCode = %s, Country = %s "
                                "WHERE LocationID = %s",
                                (
                                    new_address,
                                    new_city,
                                    new_state,
                                    new_zipcode,
                                    new_country,
                                    loc_id,
                                ),
                            )
                            conn.commit()
                            print("Address updated.\n")
                    except ValueError:
                        print("Invalid selection.\n")

            elif choice == "3":
                cur.execute(
                    "SELECT l.LocationID, l.Address, l.City, l.State, l.ZipCode, l.Country "
                    "FROM user_x_address ua JOIN locations l ON ua.LocationID = l.LocationID "
                    "WHERE ua.UserID = %s",
                    (user_id,),
                )
                rows = cur.fetchall()
                if not rows:
                    print("No addresses to delete.\n")
                else:
                    print("\nSelect address to delete:")
                    for idx, (loc_id, addr, city, state, zipcode, country) in enumerate(
                        rows, start=1
                    ):
                        print(
                            f"{idx}. {addr}, {city}, {state} {zipcode}, {country} (LocationID {loc_id})"
                        )
                    choice_idx = input("Enter number of address: ").strip()
                    try:
                        addr_idx = int(choice_idx)
                        if addr_idx < 1 or addr_idx > len(rows):
                            print("Invalid selection.\n")
                        else:
                            loc_id, addr, city, state, zipcode, country = rows[
                                addr_idx - 1
                            ]
                            cur.execute(
                                "SELECT COUNT(*) FROM card WHERE AddressID = %s",
                                (loc_id,),
                            )
                            count = cur.fetchone()[0]
                            if count > 0:
                                print(
                                    "Cannot delete address with associated cards.\n"
                                )
                            else:
                                cur.execute(
                                    "DELETE FROM user_x_address WHERE UserID = %s AND LocationID = %s",
                                    (user_id, loc_id),
                                )
                                cur.execute(
                                    "DELETE FROM locations WHERE LocationID = %s",
                                    (loc_id,),
                                )
                                conn.commit()
                                print("Address deleted.\n")
                    except ValueError:
                        print("Invalid selection.\n")

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Address error: {error}\n")
            conn.rollback()
        finally:
            cur.close()
            conn.close()


# ===================== AGENT: PROPERTY MANAGEMENT =====================

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
        cur.execute(
            """
            SELECT p.propertyid, p.type, p.description, p.price, p.availability, p.crimerate,
                   l.address, l.city, l.state, l.zipcode, l.country
            FROM property p
            JOIN locations l ON p.locationid = l.locationid
            ORDER BY l.city, l.state, p.price;
        """
        )
        rows = cur.fetchall()

        if not rows:
            print("\nThere are no properties in the system.\n")
            return

        print("\n===== All Properties =====")
        for row in rows:
            (
                pid,
                ptype,
                desc,
                price,
                avail,
                crime,
                addr,
                city,
                state,
                zipcode,
                country,
            ) = row
            print(f"Property ID: {pid}")
            print(f"  Type: {ptype}")
            print(f"  Address: {addr}, {city}, {state} {zipcode}, {country}")
            print(f"  Price: ${price:.2f}")
            print(f"  Availability: {avail}")
            print(f"  Crime Rate: {crime}")
            cur.execute(
                """
                SELECT s.name, pxs.distancemiles
                FROM property_x_school pxs
                JOIN school s ON pxs.schoolid = s.schoolid
                WHERE pxs.propertyid = %s
                ORDER BY pxs.distancemiles NULLS LAST, s.name;
                """,
                (pid,),
            )
            schools = cur.fetchall()
            if schools:
                print("  Nearby Schools:")
                for name, dist in schools:
                    if dist is None:
                        print(f"    - {name}")
                    else:
                        print(f"    - {name} ({dist} mi)")
            print("-" * 40)
        


    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error listing properties: {error}\n")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def add_property():
    """Add a new property, tie it to current agent, store listing type, and optional nearby schools."""
    global current_user
    if current_user is None or current_user.get("type") != "Agent":
        print("You must be logged in as an Agent.\n")
        return

    agent_id = current_user.get("agent_id")
    if not agent_id:
        print("Agent ID missing.\n")
        return

    conn, cur = get_connection()
    if conn is None:
        return

    try:
        print("\n===== Add New Property =====")
        address = input("Street address: ").strip()
        city = input("City: ").strip()
        state = input("State: ").strip()
        zipcode = input("Zip code: ").strip()
        country = input("Country: ").strip()

        if not (address and city and state and zipcode and country):
            print("All address fields are required.\n")
            return

        listing_type = input("Listing type (Rent/Sale) [Rent]: ").strip().title()
        if not listing_type:
            listing_type = "Rent"
        if listing_type not in ("Rent", "Sale"):
            print("Listing type must be Rent or Sale.\n")
            return

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
            "5": "VacationHome",
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

        # IMPORTANT: availability should be a *base status*, not date availability.
        # We'll use 'Active'/'Inactive' only.
        status = input("Status (Active/Inactive) [Active]: ").strip().title()
        if not status:
            status = "Active"
        if status not in ("Active", "Inactive"):
            print("Status must be Active or Inactive.\n")
            return

        crime_rate = input("Crime rate description (optional): ").strip() or None

        location_id = str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO locations (locationid, address, city, state, zipcode, country)
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (location_id, address, city, state, zipcode, country),
        )

        property_id = str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO property (propertyid, type, locationid, description, price, availability, crimerate, listingtype, agentid)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (property_id, ptype, location_id, description, price, status, crime_rate, listing_type, agent_id),
        )

        if ptype == "House":
            num_rooms = int(input("Number of rooms: ").strip())
            sqft = int(input("Square feet: ").strip())
            house_id = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO house (houseid, propertyid, numrooms, squarefeet)
                VALUES (%s, %s, %s, %s);
                """,
                (house_id, property_id, num_rooms, sqft),
            )

        elif ptype == "Apartment":
            building_type = input("Building type (e.g., 'HighRise'): ").strip()
            floor = int(input("Floor: ").strip())
            num_rooms = int(input("Number of rooms: ").strip())
            sqft = int(input("Square feet: ").strip())  # ✅ added
            apt_id = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO apartment (apartmentid, propertyid, buildingtype, floor, numrooms, squarefeet)
                VALUES (%s, %s, %s, %s, %s, %s);
                """,
                (apt_id, property_id, building_type, floor, num_rooms, sqft),
            )

        elif ptype == "CommercialBuilding":
            sqft = int(input("Square feet: ").strip())
            business_type = input("Type of business allowed (e.g., 'Retail'): ").strip()
            cb_id = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO commercialbuilding (commercialbuildingid, propertyid, squarefeet, businesstype)
                VALUES (%s, %s, %s, %s);
                """,
                (cb_id, property_id, sqft, business_type),
            )

        elif ptype == "Land":
            land_id = str(uuid.uuid4())
            cur.execute(
                "INSERT INTO land (landid, propertyid) VALUES (%s, %s);",
                (land_id, property_id),
            )

        elif ptype == "VacationHome":
            vh_id = str(uuid.uuid4())
            cur.execute(
                "INSERT INTO vacationhome (vacationhomeid, propertyid) VALUES (%s, %s);",
                (vh_id, property_id),
            )

        # ✅ Nearby schools (optional)
        add_schools = input("Add nearby schools? (y/n): ").strip().lower()
        if add_schools == "y":
            while True:
                school_name = input("School name (blank to stop): ").strip()
                if not school_name:
                    break
                dist_str = input("Distance (miles, blank if unknown): ").strip()
                dist = None
                if dist_str:
                    try:
                        dist = float(dist_str)
                    except ValueError:
                        print("Invalid distance; leaving blank.")

                # Find or create school
                cur.execute("SELECT schoolid FROM school WHERE name = %s", (school_name,))
                row = cur.fetchone()
                if row:
                    school_id = row[0]
                else:
                    school_id = str(uuid.uuid4())
                    cur.execute("INSERT INTO school (schoolid, name) VALUES (%s, %s)", (school_id, school_name))

                pxs_id = str(uuid.uuid4())
                cur.execute(
                    """
                    INSERT INTO property_x_school (propertyschoolid, propertyid, schoolid, distance_miles)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (pxs_id, property_id, school_id, dist),
                )

        conn.commit()
        print("\nProperty added successfully!\n")

    except Exception as e:
        print(f"Error adding property: {e}\n")
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

        cur.execute(
            """
            SELECT p.propertyid, p.type, p.description, p.price, p.availability, p.crimerate,
                   l.locationid, l.address, l.city, l.state, l.zipcode, l.country
            FROM property p
            JOIN locations l ON p.locationid = l.locationid
            WHERE p.propertyid = %s;
        """,
            (pid,),
        )
        row = cur.fetchone()

        if not row:
            print("No such property.\n")
            return

        (
            propertyid,
            ptype,
            desc,
            price,
            avail,
            crime,
            locid,
            address,
            city,
            state,
            zipcode,
            country,
        ) = row

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

        cur.execute(
            """
            UPDATE property
            SET description = %s, price = %s, availability = %s, crimerate = %s
            WHERE propertyid = %s;
        """,
            (new_desc, new_price, new_avail, new_crime, propertyid),
        )

        cur.execute(
            """
            UPDATE locations
            SET address = %s, city = %s, state = %s, zipcode = %s, country = %s
            WHERE locationid = %s;
        """,
            (new_address, new_city, new_state, new_zip, new_country, locid),
        )

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

        cur.execute(
            """
            SELECT COUNT(*) FROM booking WHERE propertyid = %s;
        """,
            (pid,),
        )
        count = cur.fetchone()[0]
        if count > 0:
            print("Cannot delete property with existing bookings.\n")
            return

        cur.execute(
            """
            SELECT type, locationid
            FROM property
            WHERE propertyid = %s;
        """,
            (pid,),
        )
        row = cur.fetchone()
        if not row:
            print("No such property.\n")
            return

        ptype, locid = row

        if ptype == "House":
            cur.execute("DELETE FROM house WHERE propertyid = %s;", (pid,))
        elif ptype == "Apartment":
            cur.execute("DELETE FROM apartment WHERE propertyid = %s;", (pid,))
        elif ptype == "CommercialBuilding":
            cur.execute(
                "DELETE FROM commercialbuilding WHERE propertyid = %s;", (pid,)
            )
        elif ptype == "Land":
            cur.execute("DELETE FROM land WHERE propertyid = %s;", (pid,))
        elif ptype == "VacationHome":
            cur.execute("DELETE FROM vacationhome WHERE propertyid = %s;", (pid,))

        cur.execute("DELETE FROM property WHERE propertyid = %s;", (pid,))

        # location row left intact intentionally

        conn.commit()
        print("Property deleted successfully.\n")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error deleting property: {error}\n")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


# ===================== PROPERTY SEARCH (Renter/Agent) =====================

def search_properties():
    conn, cur = get_connection()
    if conn is None:
        return

    try:
        print("\n===== Search Properties =====")
        city = input("City (blank for any): ").strip()
        state = input("State (blank for any): ").strip()
        prop_type = input("Property type (blank for any): ").strip()
        listing_type = input("Listing type Rent/Sale (blank for any): ").strip().title() 
        min_price = input("Min price (blank for any): ").strip()
        max_price = input("Max price (blank for any): ").strip()
        min_bedrooms = input("Min bedrooms (blank for any): ").strip()
        desired_date = read_date("Desired date (YYYY-MM-DD, blank for any): ")
        sort = input("Sort by price/bedrooms/none: ").strip().lower()

        query = """
            SELECT p.PropertyID,
                   p.Type,
                   p.ListingType,
                   p.Description,
                   p.Price,
                   l.City,
                   l.State,
                   COALESCE(h.NumRooms, a.NumRooms) AS Bedrooms
            FROM property p
            JOIN locations l ON p.LocationID = l.LocationID
            LEFT JOIN house h ON p.PropertyID = h.PropertyID
            LEFT JOIN apartment a ON p.PropertyID = a.PropertyID
            WHERE p.Availability = 'Active'
        """
        params = []

        if city:
            query += " AND l.City = %s"
            params.append(city)
        if state:
            query += " AND l.State = %s"
            params.append(state)
        if prop_type:
            query += " AND p.Type = %s"
            params.append(prop_type)
        if listing_type: 
            query += " AND p.ListingType = %s"
            params.append(listing_type)
        if min_price:
            query += " AND p.Price >= %s"
            params.append(min_price)
        if max_price:
            query += " AND p.Price <= %s"
            params.append(max_price)
        if min_bedrooms:
            query += " AND COALESCE(h.NumRooms, a.NumRooms) >= %s"
            params.append(min_bedrooms)
        if desired_date:
            query += """
                AND NOT EXISTS (
                    SELECT 1 FROM booking b
                    WHERE b.PropertyID = p.PropertyID
                      AND %s BETWEEN b.StartDate AND b.EndDate
                )
            """
            params.append(desired_date)

        if sort == "price":
            query += " ORDER BY p.Price"
        elif sort == "bedrooms":
            query += " ORDER BY Bedrooms"

        cur.execute(query, tuple(params))
        rows = cur.fetchall()

        if not rows:
            print("No properties found.\n")
        else:
            print("\nResults:")
            for idx, (prop_id, ptype, ltype, desc, price, c, s, beds) in enumerate(rows, start=1):
                print(f"{idx}. [{ltype}] {ptype} in {c}, {s} - ${price}, Bedrooms: {beds if beds is not None else 'N/A'}")
                print(f"   {desc} (PropertyID {prop_id})")
            print()

    except Exception as e:
        print(f"Search error: {e}\n")
        conn.rollback()
    finally:
        cur.close()
        conn.close()



# ===================== RENTER: BOOK PROPERTY & BOOKINGS =====================

def renter_book_property():
    global current_user
    if current_user is None or current_user.get("type") != "Renter":
        print("You must be logged in as a renter to book properties.\n")
        return

    renter_id = current_user.get("renter_id")
    if renter_id is None:
        conn, cur = get_connection()
        if conn is None:
            return
        try:
            cur.execute(
                "SELECT RenterID FROM renter WHERE UserID = %s",
                (current_user["user_id"],),
            )
            row = cur.fetchone()
            if row is None:
                print("No renter record found for current user.\n")
                return
            renter_id = str(row[0])
            current_user["renter_id"] = renter_id
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error loading renter info: {error}\n")
            conn.rollback()
            return
        finally:
            cur.close()
            conn.close()

    conn, cur = get_connection()
    if conn is None:
        return

    try:
        cur.execute(
            """
            SELECT p.PropertyID,
                   p.Type,
                   p.Description,
                   p.Price,
                   l.City,
                   l.State,
                   COALESCE(h.NumRooms, a.NumRooms) AS Bedrooms
            FROM property p
            JOIN locations l ON p.LocationID = l.LocationID
            LEFT JOIN house h ON p.PropertyID = h.PropertyID
            LEFT JOIN apartment a ON p.PropertyID = a.PropertyID
            WHERE p.Availability = 'Active'
        """
        )
        props = cur.fetchall()
        if not props:
            print("No available properties to book.\n")
            return

        print("\nAvailable properties:")
        for idx, (prop_id, ptype, desc, price, c, s, beds) in enumerate(
            props, start=1
        ):
            print(
                f"{idx}. {ptype} in {c}, {s} - ${price}, "
                f"Bedrooms: {beds if beds is not None else 'N/A'}"
            )
            print(f"   {desc}")

        choice = input("Select a property number to book: ").strip()
        try:
            idx = int(choice)
            if idx < 1 or idx > len(props):
                print("Invalid selection.\n")
                return
        except ValueError:
            print("Invalid selection.\n")
            return

        prop_id, ptype, desc, price, c, s, beds = props[idx - 1]

        cur.execute("SELECT AgentID FROM property WHERE PropertyID = %s", (prop_id,))
        agent_row = cur.fetchone()
        agent_id = agent_row[0] if agent_row else None


        start_str = input("Enter start date (YYYY-MM-DD): ").strip()
        end_str = input("Enter end date (YYYY-MM-DD): ").strip()
        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
            if end_date <= start_date:
                print("End date must be after start date.\n")
                return
        except ValueError:
            print("Invalid date format.\n")
            return

        cur.execute(
            "SELECT CardID, CardNumber, ExpirationDate FROM card WHERE RenterID = %s",
            (renter_id,),
        )
        cards = cur.fetchall()
        if not cards:
            print("You must add a credit card before booking.\n")
            return

        print("\nSelect payment method:")
        for i, (card_id, number, exp) in enumerate(cards, start=1):
            num_str = str(number)
            if len(num_str) > 4:
                masked = "*" * (len(num_str) - 4) + num_str[-4:]
            else:
                masked = num_str
            print(f"{i}. Card ending in {masked}, Exp {exp}")
        card_choice = input("Enter number of card: ").strip()
        try:
            card_idx = int(card_choice)
            if card_idx < 1 or card_idx > len(cards):
                print("Invalid selection.\n")
                return
        except ValueError:
            print("Invalid selection.\n")
            return

        card_id, number, exp = cards[card_idx - 1]

        days = (end_date - start_date).days
        total_cost = float(price) * days

        print("\nBooking summary:")
        print(f"Property: {ptype} in {c}, {s}")
        print(f"Dates: {start_date} to {end_date} ({days} days)")
        print(f"Total cost: ${total_cost}")
        print(f"Payment method: card ending in {str(number)[-4:]}")

        confirm = input("Confirm booking? (y/n): ").strip().lower()
        if confirm != "y":
            print("Booking cancelled.\n")
            return

        cur.execute(
            """
            SELECT COUNT(*) FROM booking
            WHERE PropertyID = %s
              AND NOT (EndDate < %s OR StartDate > %s)
            """,
            (prop_id, start_date, end_date),
        )
        if cur.fetchone()[0] > 0:
            print("Property already booked for that period.\n")
            return

        booking_id = str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO booking (BookingID, CardID, RenterID, AgentID, PropertyID, StartDate, EndDate)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (booking_id, card_id, renter_id, agent_id, prop_id, start_date, end_date),
        )

        cur.execute("SELECT points FROM rewards_member WHERE renterid = %s", (renter_id,))
        rm = cur.fetchone()
        if rm is not None:
            points_earned = int(total_cost)
            cur.execute(
                "UPDATE rewards_member SET points = points + %s WHERE renterid = %s",
                (points_earned, renter_id),
            )
            print(f"Rewards: +{points_earned} points!")

        conn.commit()
        print("Booking created.\n")


    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Booking error: {error}\n")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def renter_manage_bookings():
    """Renter: view and cancel own bookings."""
    global current_user
    if current_user is None:
        print("You must be logged in to manage bookings.\n")
        return

    if current_user.get("type") == "Agent":
        print("Agent booking management not implemented here (use agent menu).\n")
        return

    renter_id = current_user.get("renter_id")
    if renter_id is None:
        conn, cur = get_connection()
        if conn is None:
            return
        try:
            cur.execute(
                "SELECT RenterID FROM renter WHERE UserID = %s",
                (current_user["user_id"],),
            )
            row = cur.fetchone()
            if row is None:
                print("No renter record found for current user.\n")
                return
            renter_id = str(row[0])
            current_user["renter_id"] = renter_id
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error loading renter info: {error}\n")
            conn.rollback()
            return
        finally:
            cur.close()
            conn.close()

    while True:
        print("\n===== My Bookings =====")
        print("1. View My Bookings")
        print("2. Cancel Booking")
        print("0. Back")

        choice = input("Select an option: ").strip()

        if choice == "0":
            break

        conn, cur = get_connection()
        if conn is None:
            return

        try:
            if choice == "1":
                cur.execute(
                    """
                    SELECT b.BookingID,
                           p.PropertyID,
                           p.Type,
                           p.Description,
                           p.Price,
                           b.StartDate,
                           b.EndDate,
                           l.City,
                           l.State,
                           c.CardNumber
                    FROM booking b
                    JOIN property p ON b.PropertyID = p.PropertyID
                    JOIN locations l ON p.LocationID = l.LocationID
                    JOIN card c ON b.CardID = c.CardID
                    WHERE b.RenterID = %s
                """,
                    (renter_id,),
                )
                rows = cur.fetchall()
                if not rows:
                    print("No bookings found.\n")
                else:
                    print()
                    for idx, (
                        book_id,
                        prop_id,
                        ptype,
                        desc,
                        price,
                        start,
                        end,
                        c,
                        s,
                        card_num,
                    ) in enumerate(rows, start=1):
                        days = (end - start).days
                        total_cost = float(price) * days
                        num_str = str(card_num)
                        if len(num_str) > 4:
                            masked = "*" * (len(num_str) - 4) + num_str[-4:]
                        else:
                            masked = num_str
                        print(f"{idx}. {ptype} in {c}, {s}")
                        print(
                            f"   {start} to {end} ({days} days), Total ${total_cost}, Card {masked}"
                        )
                        print(f"   {desc} (BookingID {book_id})")
                    print()

            elif choice == "2":
                cur.execute(
                    """
                    SELECT b.BookingID,
                           p.PropertyID,
                           p.Type,
                           p.Description,
                           p.Price,
                           b.StartDate,
                           b.EndDate,
                           l.City,
                           l.State
                    FROM booking b
                    JOIN property p ON b.PropertyID = p.PropertyID
                    JOIN locations l ON p.LocationID = l.LocationID
                    WHERE b.RenterID = %s
                """,
                    (renter_id,),
                )
                rows = cur.fetchall()
                if not rows:
                    print("No bookings to cancel.\n")
                else:
                    print("\nSelect booking to cancel:")
                    for idx, (
                        book_id,
                        prop_id,
                        ptype,
                        desc,
                        price,
                        start,
                        end,
                        c,
                        s,
                    ) in enumerate(rows, start=1):
                        print(
                            f"{idx}. {ptype} in {c}, {s} from {start} to {end}"
                        )
                    choice_idx = input("Enter number of booking: ").strip()
                    try:
                        b_idx = int(choice_idx)
                        if b_idx < 1 or b_idx > len(rows):
                            print("Invalid selection.\n")
                        else:
                            (
                                book_id,
                                prop_id,
                                ptype,
                                desc,
                                price,
                                start,
                                end,
                                c,
                                s,
                            ) = rows[b_idx - 1]
                            confirm = input(
                                "Are you sure you want to cancel this booking? (y/n): "
                            ).strip().lower()
                            if confirm == "y":
                                cur.execute(
                                    "DELETE FROM booking WHERE BookingID = %s AND RenterID = %s",
                                    (book_id, renter_id),
                                )
                                cur.execute(
                                    "UPDATE property SET Availability = 'Active' WHERE PropertyID = %s",
                                    (prop_id,),
                                )
                                conn.commit()
                                print(
                                    "Booking cancelled. Refund will be issued to your saved payment method.\n"
                                )
                    except ValueError:
                        print("Invalid selection.\n")

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Booking management error: {error}\n")
            conn.rollback()
        finally:
            cur.close()
            conn.close()


# ===================== AGENT: BOOKINGS (from your version) =====================

def manage_agent_bookings():
    """Agent: view and cancel bookings for properties under their agency."""
    global current_user
    agent_id = current_user.get("agent_id") if current_user else None
    if not agent_id:
        print("Agent ID not found for current user.\n")
        return

    conn, cur = get_connection()
    if conn is None:
        return

    try:
        while True:
            print("\n===== Bookings for My Agency =====")

            cur.execute(
                """
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
                WHERE p.agentid = %s
                ORDER BY b.startdate DESC;
                """,
                (agent_id,),
            )

            rows = cur.fetchall()

            if not rows:
                print("There are no bookings associated with your agency.\n")
            else:
                for row in rows:
                    (
                        bookingid,
                        pid,
                        ptype,
                        desc,
                        price,
                        addr,
                        city,
                        state,
                        zipcode,
                        startdate,
                        enddate,
                        renter_name,
                        renter_email,
                        cardnumber,
                    ) = row
                    masked_card = "**** **** **** " + cardnumber[-4:]
                    print(f"Booking ID: {bookingid}")
                    print(f"  Property: {ptype} ({pid})")
                    print(
                        f"  Address: {addr}, {city}, {state} {zipcode}"
                    )
                    print(f"  Description: {desc}")
                    print(f"  Price (per period unit): ${price:.2f}")
                    print(f"  Rental Period: {startdate} to {enddate}")
                    print(
                        f"  Renter: {renter_name} <{renter_email}>"
                    )
                    print(f"  Payment Method: {masked_card}")
                    print("-" * 40)

            print("1. Cancel a booking")
            print("0. Back")
            choice = input("Select an option: ").strip()

            if choice == "1":
                bid = input(
                    "Enter Booking ID to cancel (or blank to cancel): "
                ).strip()
                if not bid:
                    continue

                cur.execute(
                    """
                    DELETE FROM booking b
                    USING property p
                    WHERE b.propertyid = p.propertyid
                    AND b.bookingid = %s
                    AND p.agentid = %s;
                    """,
                    (bid, agent_id),
                )

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


def manage_bookings():
    """
    View / cancel bookings.

    - Renters: their own bookings (renter_manage_bookings).
    - Agents: bookings for properties under their agency (manage_agent_bookings).
    """
    global current_user

    if current_user is None:
        print("You must be logged in to manage bookings.\n")
        return

    user_type = current_user.get("type")

    if user_type == "Renter":
        renter_manage_bookings()
    elif user_type == "Agent":
        manage_agent_bookings()
    else:
        print("Unknown user type.\n")


# ===================== REWARDS PROGRAM =====================

def renter_rewards_menu():
    global current_user
    if current_user is None or current_user.get("type") != "Renter":
        print("Login as renter.\n")
        return
    renter_id = current_user.get("renter_id")
    if not renter_id:
        print("Renter ID missing.\n")
        return

    conn, cur = get_connection()
    if conn is None:
        return
    try:
        while True:
            cur.execute("SELECT points, joinedat FROM rewards_member WHERE renterid = %s", (renter_id,))
            row = cur.fetchone()

            print("\n===== Rewards Program =====")
            if row:
                pts, joined = row
                print(f"Status: Member since {joined}")
                print(f"Points: {pts}")
                print("1. Leave rewards program")
            else:
                print("Status: Not a member")
                print("1. Join rewards program")
            print("0. Back")

            choice = input("Select: ").strip()
            if choice == "0":
                break

            if not row and choice == "1":
                cur.execute("INSERT INTO rewards_member (renterid, points) VALUES (%s, 0)", (renter_id,))
                conn.commit()
                print("Joined rewards program.\n")
            elif row and choice == "1":
                cur.execute("DELETE FROM rewards_member WHERE renterid = %s", (renter_id,))
                conn.commit()
                print("Left rewards program.\n")
            else:
                print("Invalid.\n")
    except Exception as e:
        print(f"Rewards error: {e}\n")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


# ===================== MENUS =====================

def renter_menu():
    """Menu for logged-in renters."""
    while True:
        print("\n===== Renter Menu =====")
        print("1. Manage Payment Information")
        print("2. Manage Addresses")
        print("3. Search Properties")
        print("4. Book a Property")
        print("5. View/Cancel My Bookings")
        print("6. Rewards Program")
        print("7. Logout")
        print("0. Exit Program")

        choice = input("Select an option: ").strip()

        if choice == "1":
            renter_manage_payment_info()
        elif choice == "2":
            renter_manage_addresses()
        elif choice == "3":
            search_properties()
        elif choice == "4":
            renter_book_property()
        elif choice == "5":
            manage_bookings()
        elif choice == "6":
            renter_rewards_menu()
        elif choice == "7":
            logout()
            break
        elif choice == "0":
            print("Exiting program.")
            exit(0)
        else:
            print("Invalid option.\n")


def agent_menu():
    """Menu for logged-in agents."""
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
    """Top-level menu."""
    global current_user
    while True:
        print("\n===== Real Estate Booking System =====")

        if current_user is None:
            print("1. Register Account")
            print("2. Login")
            print("0. Exit")

            choice = input("Select an option: ").strip()

            if choice == "1":
                register_account()
            elif choice == "2":
                if login():
                    if current_user["type"] == "Renter":
                        renter_menu()
                    elif current_user["type"] == "Agent":
                        agent_menu()
            elif choice == "0":
                print("Exiting program.")
                break
            else:
                print("Invalid option.\n")
        else:
            print("Already logged in. Use logout from your menu.")
            # Let them go to their menu directly
            if current_user["type"] == "Renter":
                renter_menu()
            elif current_user["type"] == "Agent":
                agent_menu()


if __name__ == "__main__":
    main_menu()

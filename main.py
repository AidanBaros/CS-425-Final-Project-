import psycopg2
import uuid
from datetime import datetime

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


def get_connection():
    """ Connect to the PostgreSQL database server """
    try:
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(host="localhost", 
                                database="My Database",
                                user="My Database", 
                                password="1234",
                                port=5432)

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
            cur.execute("SELECT RenterID FROM renter WHERE UserID = %s", (current_user["user_id"],))
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
            # cursor
            if choice == "4":
                cur.execute(
                    "SELECT CardID, CardNumber, ExpirationDate, CVV, AddressID "
                    "FROM card WHERE RenterID = %s",
                    (renter_id,)
                )
                rows = cur.fetchall()
                if not rows:
                    print("No cards found.\n")
                else:
                    print("\nYour cards:")
                    for idx, (card_id, number, exp, cvv, addr_id) in enumerate(rows, start=1):
                        num_str = str(number)
                        if len(num_str) > 4:
                            masked = "*" * (len(num_str) - 4) + num_str[-4:]
                        else:
                            masked = num_str
                        print(f"{idx}. CardID {card_id}, Number {masked}, Exp {exp}, AddressID {addr_id}")
                    print()

            elif choice == "1":
                cur.execute(
                    "SELECT l.LocationID, l.Address, l.City, l.State, l.ZipCode, l.Country "
                    "FROM user_x_address ua JOIN locations l ON ua.LocationID = l.LocationID "
                    "WHERE ua.UserID = %s",
                    (current_user["user_id"],)
                )
                addresses = cur.fetchall()
                if not addresses:
                    print("You must add an address before adding a card.\n")
                else:
                    print("\nSelect billing address:")
                    for idx, row in enumerate(addresses, start=1):
                        loc_id, addr, city, state, zipcode, country = row
                        print(f"{idx}. {addr}, {city}, {state} {zipcode}, {country} (LocationID {loc_id})")
                    addr_choice = input("Enter number of billing address: ").strip()
                    try:
                        addr_idx = int(addr_choice)
                        if addr_idx < 1 or addr_idx > len(addresses):
                            print("Invalid selection.\n")
                        else:
                            location_id = addresses[addr_idx - 1][0]
                            card_number = input("Enter card number: ").strip()
                            expiration_date = input("Enter expiration date (YYYY-MM-DD): ").strip()
                            cvv = input("Enter CVV: ").strip()
                            card_id = str(uuid.uuid4())
                            cur.execute(
                                "INSERT INTO card (CardID, RenterID, AddressID, CardNumber, ExpirationDate, CVV) "
                                "VALUES (%s, %s, %s, %s, %s, %s)",
                                (card_id, renter_id, location_id, card_number, expiration_date, cvv)
                            )
                            conn.commit()
                            print("Card added.\n")
                    except ValueError:
                        print("Invalid selection.\n")

            elif choice == "2":
                cur.execute(
                    "SELECT CardID, CardNumber, ExpirationDate, CVV, AddressID "
                    "FROM card WHERE RenterID = %s",
                    (renter_id,)
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
                        print(f"{idx}. CardID {card_id}, Number {masked}, Exp {exp}")
                    card_choice = input("Enter number of card: ").strip()
                    try:
                        card_idx = int(card_choice)
                        if card_idx < 1 or card_idx > len(cards):
                            print("Invalid selection.\n")
                        else:
                            card_id, number, exp, cvv, addr_id = cards[card_idx - 1]
                            new_number = input("Enter new card number (leave blank to keep current): ").strip()
                            new_exp = input("Enter new expiration date YYYY-MM-DD (leave blank to keep current): ").strip()
                            new_cvv = input("Enter new CVV (leave blank to keep current): ").strip()
                            if not new_number:
                                new_number = number
                            if not new_exp:
                                new_exp = exp
                            if not new_cvv:
                                new_cvv = cvv
                            cur.execute(
                                "UPDATE card SET CardNumber = %s, ExpirationDate = %s, CVV = %s "
                                "WHERE CardID = %s AND RenterID = %s",
                                (new_number, new_exp, new_cvv, card_id, renter_id)
                            )
                            conn.commit()
                            print("Card updated.\n")
                    except ValueError:
                        print("Invalid selection.\n")

            elif choice == "3":
                cur.execute(
                    "SELECT CardID, CardNumber, ExpirationDate, CVV, AddressID "
                    "FROM card WHERE RenterID = %s",
                    (renter_id,)
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
                        print(f"{idx}. CardID {card_id}, Number {masked}, Exp {exp}")
                    card_choice = input("Enter number of card: ").strip()
                    try:
                        card_idx = int(card_choice)
                        if card_idx < 1 or card_idx > len(cards):
                            print("Invalid selection.\n")
                        else:
                            card_id, number, exp, cvv, addr_id = cards[card_idx - 1]
                            cur.execute(
                                "SELECT COUNT(*) FROM booking WHERE CardID = %s",
                                (card_id,)
                            )
                            count = cur.fetchone()[0]
                            if count > 0:
                                print("Cannot delete card with active bookings.\n")
                            else:
                                cur.execute(
                                    "DELETE FROM card WHERE CardID = %s AND RenterID = %s",
                                    (card_id, renter_id)
                                )
                                conn.commit()
                                print("Card deleted.\n")
                    except ValueError:
                        print("Invalid selection.\n")

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Payment error: {error}\n")
            conn.rollback()
        finally:
            # Close the cursor
            cur.close()
            # Close the Connection
            conn.close()

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
            # cursor
            if choice == "4":
                cur.execute(
                    "SELECT l.LocationID, l.Address, l.City, l.State, l.ZipCode, l.Country "
                    "FROM user_x_address ua JOIN locations l ON ua.LocationID = l.LocationID "
                    "WHERE ua.UserID = %s",
                    (user_id,)
                )
                rows = cur.fetchall()
                if not rows:
                    print("No addresses found.\n")
                else:
                    print("\nYour addresses:")
                    for idx, (loc_id, addr, city, state, zipcode, country) in enumerate(rows, start=1):
                        print(f"{idx}. {addr}, {city}, {state} {zipcode}, {country} (LocationID {loc_id})")
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
                        (location_id, address, city, state, zipcode, country)
                    )
                    user_address_id = str(uuid.uuid4())
                    cur.execute(
                        "INSERT INTO user_x_address (UserAddressID, UserID, LocationID) "
                        "VALUES (%s, %s, %s)",
                        (user_address_id, user_id, location_id)
                    )
                    conn.commit()
                    print("Address added.\n")

            elif choice == "2":
                cur.execute(
                    "SELECT l.LocationID, l.Address, l.City, l.State, l.ZipCode, l.Country "
                    "FROM user_x_address ua JOIN locations l ON ua.LocationID = l.LocationID "
                    "WHERE ua.UserID = %s",
                    (user_id,)
                )
                rows = cur.fetchall()
                if not rows:
                    print("No addresses to modify.\n")
                else:
                    print("\nSelect address to modify:")
                    for idx, (loc_id, addr, city, state, zipcode, country) in enumerate(rows, start=1):
                        print(f"{idx}. {addr}, {city}, {state} {zipcode}, {country} (LocationID {loc_id})")
                    choice_idx = input("Enter number of address: ").strip()
                    try:
                        addr_idx = int(choice_idx)
                        if addr_idx < 1 or addr_idx > len(rows):
                            print("Invalid selection.\n")
                        else:
                            loc_id, addr, city, state, zipcode, country = rows[addr_idx - 1]
                            new_address = input("Enter new street address (leave blank to keep current): ").strip()
                            new_city = input("Enter new city (leave blank to keep current): ").strip()
                            new_state = input("Enter new state (leave blank to keep current): ").strip()
                            new_zipcode = input("Enter new zip code (leave blank to keep current): ").strip()
                            new_country = input("Enter new country (leave blank to keep current): ").strip()
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
                                (new_address, new_city, new_state, new_zipcode, new_country, loc_id)
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
                    (user_id,)
                )
                rows = cur.fetchall()
                if not rows:
                    print("No addresses to delete.\n")
                else:
                    print("\nSelect address to delete:")
                    for idx, (loc_id, addr, city, state, zipcode, country) in enumerate(rows, start=1):
                        print(f"{idx}. {addr}, {city}, {state} {zipcode}, {country} (LocationID {loc_id})")
                    choice_idx = input("Enter number of address: ").strip()
                    try:
                        addr_idx = int(choice_idx)
                        if addr_idx < 1 or addr_idx > len(rows):
                            print("Invalid selection.\n")
                        else:
                            loc_id, addr, city, state, zipcode, country = rows[addr_idx - 1]
                            cur.execute(
                                "SELECT COUNT(*) FROM card WHERE AddressID = %s",
                                (loc_id,)
                            )
                            count = cur.fetchone()[0]
                            if count > 0:
                                print("Cannot delete address with associated cards.\n")
                            else:
                                cur.execute(
                                    "DELETE FROM user_x_address WHERE UserID = %s AND LocationID = %s",
                                    (user_id, loc_id)
                                )
                                cur.execute(
                                    "DELETE FROM locations WHERE LocationID = %s",
                                    (loc_id,)
                                )
                                conn.commit()
                                print("Address deleted.\n")
                    except ValueError:
                        print("Invalid selection.\n")

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Address error: {error}\n")
            conn.rollback()
        finally:
            # Close the cursor
            cur.close()
            # Close the Connection
            conn.close()

def manage_properties():

    print("Functionality not implemented yet.\n")

def search_properties():
    conn, cur = get_connection()
    if conn is None:
        return

    try:
        print("\n===== Search Properties =====")
        city = input("City (blank for any): ").strip()
        state = input("State (blank for any): ").strip()
        prop_type = input("Property type (blank for any): ").strip()
        min_price = input("Min price (blank for any): ").strip()
        max_price = input("Max price (blank for any): ").strip()
        min_bedrooms = input("Min bedrooms (blank for any): ").strip()
        desired_str = input("Desired date (YYYY-MM-DD, blank for any): ").strip()
        sort = input("Sort by price/bedrooms/none: ").strip().lower()

        desired_date = None
        if desired_str:
            try:
                desired_date = datetime.strptime(desired_str, "%Y-%m-%d").date()
            except ValueError:
                print("Invalid date format, ignoring desired date filter.\n")

        query = """
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
            WHERE p.Availability = 'Available'
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
            query += " AND NOT EXISTS (SELECT 1 FROM booking b WHERE b.PropertyID = p.PropertyID AND %s BETWEEN b.StartDate AND b.EndDate)"
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
            for idx, (prop_id, ptype, desc, price, c, s, beds) in enumerate(rows, start=1):
                print(f"{idx}. {ptype} in {c}, {s} - ${price}, Bedrooms: {beds if beds is not None else 'N/A'}")
                print(f"   {desc} (PropertyID {prop_id})")
            print()

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Search error: {error}\n")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

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
            cur.execute("SELECT RenterID FROM renter WHERE UserID = %s", (current_user["user_id"],))
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
        cur.execute("""
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
            WHERE p.Availability = 'Available'
        """)
        props = cur.fetchall()
        if not props:
            print("No available properties to book.\n")
            return

        print("\nAvailable properties:")
        for idx, (prop_id, ptype, desc, price, c, s, beds) in enumerate(props, start=1):
            print(f"{idx}. {ptype} in {c}, {s} - ${price}, Bedrooms: {beds if beds is not None else 'N/A'}")
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
            (renter_id,)
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
            (prop_id, start_date, end_date)
        )
        if cur.fetchone()[0] > 0:
            print("Property already booked for that period.\n")
            return

        booking_id = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO booking (BookingID, CardID, RenterID, AgentID, PropertyID, StartDate, EndDate) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (booking_id, card_id, renter_id, None, prop_id, start_date, end_date)
        )
        cur.execute(
            "UPDATE property SET Availability = 'Unavailable' WHERE PropertyID = %s",
            (prop_id,)
        )
        conn.commit()
        print("Booking created.\n")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Booking error: {error}\n")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def renter_manage_bookings():
    global current_user
    if current_user is None:
        print("You must be logged in to manage bookings.\n")
        return

    if current_user.get("type") == "Agent":
        print("Agent booking management not implemented yet.\n")
        return

    renter_id = current_user.get("renter_id")
    if renter_id is None:
        conn, cur = get_connection()
        if conn is None:
            return
        try:
            cur.execute("SELECT RenterID FROM renter WHERE UserID = %s", (current_user["user_id"],))
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
                cur.execute("""
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
                """, (renter_id,))
                rows = cur.fetchall()
                if not rows:
                    print("No bookings found.\n")
                else:
                    print()
                    for idx, (book_id, prop_id, ptype, desc, price, start, end, c, s, card_num) in enumerate(rows, start=1):
                        days = (end - start).days
                        total_cost = float(price) * days
                        num_str = str(card_num)
                        if len(num_str) > 4:
                            masked = "*" * (len(num_str) - 4) + num_str[-4:]
                        else:
                            masked = num_str
                        print(f"{idx}. {ptype} in {c}, {s}")
                        print(f"   {start} to {end} ({days} days), Total ${total_cost}, Card {masked}")
                        print(f"   {desc} (BookingID {book_id})")
                    print()

            elif choice == "2":
                cur.execute("""
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
                """, (renter_id,))
                rows = cur.fetchall()
                if not rows:
                    print("No bookings to cancel.\n")
                else:
                    print("\nSelect booking to cancel:")
                    for idx, (book_id, prop_id, ptype, desc, price, start, end, c, s) in enumerate(rows, start=1):
                        print(f"{idx}. {ptype} in {c}, {s} from {start} to {end}")
                    choice_idx = input("Enter number of booking: ").strip()
                    try:
                        b_idx = int(choice_idx)
                        if b_idx < 1 or b_idx > len(rows):
                            print("Invalid selection.\n")
                        else:
                            book_id, prop_id, ptype, desc, price, start, end, c, s = rows[b_idx - 1]
                            confirm = input("Are you sure you want to cancel this booking? (y/n): ").strip().lower()
                            if confirm == "y":
                                cur.execute(
                                    "DELETE FROM booking WHERE BookingID = %s AND RenterID = %s",
                                    (book_id, renter_id)
                                )
                                cur.execute(
                                    "UPDATE property SET Availability = 'Available' WHERE PropertyID = %s",
                                    (prop_id,)
                                )
                                conn.commit()
                                print("Booking cancelled. Refund will be issued to your saved payment method.\n")
                    except ValueError:
                        print("Invalid selection.\n")

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Booking management error: {error}\n")
            conn.rollback()
        finally:
            cur.close()
            conn.close()

def agent_add_property():
    # agent add property implementation
    pass

def agent_modify_property():
    # agent modify property implementation
    pass

def agent_delete_property():
    # agent delete property implementation
    pass

def agent_view_properties():
    # agent view properties implementation
    pass

def agent_view_bookings():
    # agent view bookings implementation
    pass

def agent_cancel_booking():
    # agent cancel booking implementation
    pass

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
            renter_manage_payment_info()
        elif choice == "2":
            renter_manage_addresses()
        elif choice == "3":
            search_properties()
        elif choice == "4":
            renter_book_property()
        elif choice == "5":
            renter_manage_bookings()
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
        print("1. Add Property")
        print("2. Modify Property")
        print("3. Delete Property")
        print("4. View My Properties")
        print("5. Search Properties")
        print("6. View/Cancel Bookings (My Properties)")
        print("7. Logout")
        print("0. Exit Program")

        choice = input("Select an option: ").strip()

        if choice == "1":
            agent_add_property()
        elif choice == "2":
            agent_modify_property()
        elif choice == "3":
            agent_delete_property()
        elif choice == "4":
            agent_view_properties()
        elif choice == "5":
            search_properties()
        elif choice == "6":
            while True:
                print("\n===== Agent Bookings =====")
                print("1. View Bookings")
                print("2. Cancel Booking")
                print("0. Back")
                sub = input("Select an option: ").strip()
                if sub == "1":
                    agent_view_bookings()
                elif sub == "2":
                    agent_cancel_booking()
                elif sub == "0":
                    break
                else:
                    print("Invalid option.\n")
        elif choice == "7":
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

if __name__ == "__main__":
    main_menu()
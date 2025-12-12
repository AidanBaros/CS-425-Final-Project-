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


def manage_payment_info():

    print("Functionality not implemented yet.\n")

def manage_addresses():

    print("Functionality not implemented yet.\n")

def manage_properties():

    print("Functionality not implemented yet.\n")

def search_properties():

    print("Functionality not implemented yet.\n")

def book_property():

    print("Functionality not implemented yet.\n")

def manage_bookings():

    print("Functionality not implemented yet.\n")

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
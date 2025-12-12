import psycopg2

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

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(host="localhost", 
                                database="postgres",
                                user="postgres", 
                                password="postgres",
                                port=5433
                                )
        cur = conn.cursor()
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')
        db_version = cur.fetchone()
        print(db_version)
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

def register_account():
    print("Functionality not implemented yet.\n")

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

def main_menu():
    # first user login, then we continue to user menu depending on user type
    
    while True:
        connect()
        print("===== Real Estate Booking System =====")
        print("1. Register Account")
        print("2. Manage Payment Information")
        print("3. Manage Addresses")
        print("4. Add/Delete/Modify Properties (Agent Only)")
        print("5. Search Properties")
        print("6. Book a Property")
        print("7. View/Cancel Bookings")
        print("0. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            register_account()
        elif choice == "2":
            manage_payment_info()
        elif choice == "3":
            manage_addresses()
        elif choice == "4":
            manage_properties()
        elif choice == "5":
            search_properties()
        elif choice == "6":
            book_property()
        elif choice == "7":
            manage_bookings()
        elif choice == "0":
            print("Exiting program.")
            break
        else:
            print("Invalid option.\n")

if __name__ == "__main__":
    main_menu()

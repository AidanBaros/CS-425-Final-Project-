import subprocess
import dotenv
import os

dotenv.load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("dbname"),
    "user": os.getenv("user"),
    "password": os.getenv("password"),
    "host": os.getenv("host"),
    "port": os.getenv("port")
}

SQL_DIR = "SQL/tables"

SQL_FILES = [
    "property.sql",
    "user.sql",
    "locations.sql",
    "agent.sql",
    "renter.sql",
    "school.sql",
    "house.sql",
    "apartment.sql",
    "commercialBuilding.sql",
    "land.sql",
    "vacationHome.sql",
    "card.sql",
    "user_x_address.sql",
    "booking.sql",
]


def run_sql_file(filename):
    path = os.path.join(SQL_DIR, filename)
    print(f"🏃 Running {filename} ...")
    result = subprocess.run(
        ["psql", "-U", DB_CONFIG["user"], "-d", DB_CONFIG["dbname"], "-f", path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"❌ Error in {filename}:\n{result.stderr}")
        raise SystemExit(1)
    else:
        print(f"✅ {filename} executed successfully.\n")

def main():
    for file in SQL_FILES:
        run_sql_file(file)
    print("🎉 All SQL files executed successfully!")

if __name__ == "__main__":
    main()

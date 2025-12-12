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

# Connects to the PostgreSQL database and runs the given SQL file
def run_sql_file():
    env = os.environ.copy()
    if DB_CONFIG["password"]:
        env["PGPASSWORD"] = DB_CONFIG["password"]

    command = [
        "psql",
        "-U", DB_CONFIG["user"],
        "-d", DB_CONFIG["dbname"],
        "-h", DB_CONFIG["host"],
        "-p", str(DB_CONFIG["port"]),
        "-f", "tables.sql",
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=env,
    )

    if result.returncode != 0:
        print(f"Error in {result.stderr}")
        raise SystemExit(1)
    else:
        print("tables.sql executed successfully.\n")


def main():
    run_sql_file()
    print("All Tables created successfully!")

if __name__ == "__main__":
    main()


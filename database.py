import sqlite3
import pandas as pd
import os

# File paths for the CSV files
CSV_FILES = {
    "hitters": "hitters_data_cleaned.csv",
    "pitchers": "pitchers_data_cleaned.csv",
    "team_standings": "team_standings_data_cleaned.csv",
    "hitter_leaderboard": "hitter_leaderboard_data_cleaned.csv",
    "pitcher_leaderboard": "pitcher_leaderboard_data_cleaned.csv",
}

DB_FILE = "sports_data.db"


def import_csv_to_sqlite(csv_files, db_file):
    """
    Import CSV files into a SQLite database as separate tables.
    :param csv_files: Dictionary of table names and their corresponding CSV file paths.
    :param db_file: Path to the SQLite database file.
    """
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to SQLite database: {db_file}")

        for table_name, file_path in csv_files.items():
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                continue

            try:
                # Load the CSV into a DataFrame
                df = pd.read_csv(file_path)

                # Import the DataFrame into the SQLite database
                df.to_sql(table_name, conn, if_exists="replace", index=False)
                print(f"Imported {file_path} into table '{table_name}'")
            except Exception as e:
                print(f"Error importing {file_path} into table '{table_name}': {e}")

        conn.close()
        print("Database import completed.")
    except Exception as e:
        print(f"Error connecting to SQLite database: {e}")


def query_database(db_file):
    """
    Query the SQLite database via the command line.
    :param db_file: Path to the SQLite database file.
    """
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to SQLite database: {db_file}")

        print("\nWelcome to the Database Query Program!")
        print("Type your SQL query below or type 'exit' to quit.")

        while True:
            query = input("\nEnter SQL query: ").strip()
            if query.lower() == "exit":
                print("Exiting the program.")
                break

            try:
                # Execute the query
                result = pd.read_sql_query(query, conn)

                # Display the results
                if result.empty:
                    print("Query executed successfully, but no results found.")
                else:
                    print(result)
            except Exception as e:
                print(f"Error executing query: {e}")

        conn.close()
        print("Disconnected from the database.")
    except Exception as e:
        print(f"Error connecting to SQLite database: {e}")


if __name__ == "__main__":
    # Step 1: Import CSV files into SQLite database
    import_csv_to_sqlite(CSV_FILES, DB_FILE)

    # Step 2: Query the database via the command line
    query_database(DB_FILE)

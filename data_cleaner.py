import pandas as pd

# File paths for the CSV files
CSV_FILES = {
    "hitters": "hitters_data.csv",
    "pitchers": "pitchers_data.csv",
    "team_standings": "team_standings_data.csv",
    "hitter_leaderboard": "hitter_leaderboard_data.csv",
    "pitcher_leaderboard": "pitcher_leaderboard_data.csv",
}


def clean_hitters(df):
    """
    Clean the hitters DataFrame.
    :param df: DataFrame containing hitters data.
    :return: Cleaned DataFrame.
    """
    # Drop rows with missing values in critical columns
    df = df.dropna(subset=["name", "team"])
    # Remove duplicates
    df = df.drop_duplicates()
    return df


def clean_pitchers(df):
    """
    Clean the pitchers DataFrame.
    :param df: DataFrame containing pitchers data.
    :return: Cleaned DataFrame.
    """
    # Drop rows with missing values in critical columns
    df = df.dropna(subset=["name", "team"])
    # Remove duplicates
    df = df.drop_duplicates()
    # Reset index
    df = df.reset_index(drop=True)
    return df


def clean_team_standings(df):
    """
    Clean the team standings DataFrame.
    :param df: DataFrame containing team standings data.
    :return: Cleaned DataFrame.
    """

    # Function to fix misaligned rows
    def fix_misaligned_row(row):
        if pd.isna(row["team_roster"]) or row["team_roster"] == "":
            # Attempt to infer the team_roster from other columns
            if pd.notna(row["wins"]) and isinstance(row["wins"], str):
                row["team_roster"] = row["wins"]
                row["wins"] = row["losses"]
                row["losses"] = row["win_percentage"]
                row["win_percentage"] = row["games_behind"]
                row["games_behind"] = None
        elif row["team_roster"] in ["East", "West"]:
            # Retain rows with East/West in team_roster without dropping them
            pass  # No changes needed; keep the row as is
        return row

    # Apply the fix for misaligned rows
    df = df.apply(fix_misaligned_row, axis=1)

    # Keep rows where team_roster is not purely numeric
    df = df.loc[df["team_roster"].astype(str).str.isnumeric() == False]

    # Ensure numeric columns are properly converted
    df["wins"] = pd.to_numeric(df["wins"], errors="coerce")
    df["losses"] = pd.to_numeric(df["losses"], errors="coerce")
    df["win_percentage"] = pd.to_numeric(df["win_percentage"], errors="coerce")
    df["games_behind"] = pd.to_numeric(
        df["games_behind"].astype(str).str.replace("½", ".5"), errors="coerce"
    )

    # Drop rows with missing or invalid numeric data
    df = df.dropna(subset=["wins", "losses", "win_percentage"])

    # Remove duplicates
    df = df.drop_duplicates()

    # Reset the index
    df = df.reset_index(drop=True)

    return df


def clean_leaderboard(df):
    """
    Clean the leaderboard DataFrame (hitter or pitcher).
    :param df: DataFrame containing leaderboard data.
    :return: Cleaned DataFrame.
    """

    # Define the expected columns
    expected_columns = ["id", "year", "statistic", "team", "value"]

    # Check if the DataFrame is empty
    if df.empty:
        print("The leaderboard DataFrame is empty. Skipping cleaning.")
        return df

    # Drop rows with extra columns by ensuring the DataFrame has exactly the expected columns
    try:
        df = df.iloc[:, : len(expected_columns)]  # Keep only the first N columns
        df.columns = expected_columns
    except Exception as e:
        print("Error while renaming columns:", e)
        print("DataFrame shape at error:", df.shape)
        return df

    # Drop rows with missing values in critical columns
    df = df.dropna(subset=["statistic", "team", "value"])

    # Ensure "value" is numeric where applicable
    try:
        df["value"] = (
            df["value"]
            .astype(str)
            .str.replace(",", "")  # Remove commas
            .str.replace('"', "")  # Remove quotes
            .str.strip()  # Remove leading/trailing whitespace
        )
        df["value"] = pd.to_numeric(df["value"], errors="coerce")  # Convert to numeric
    except Exception as e:
        print("Error while converting 'value' to numeric:", e)

    # Remove duplicates
    df = df.drop_duplicates()

    # Reset the index
    df = df.reset_index(drop=True)

    return df


def load_csv_with_fallback(file_path, expected_columns):
    """
    Load a CSV file and ensure it has the expected columns.
    Handles inconsistent rows by dynamically adjusting columns.
    :param file_path: Path to the CSV file.
    :param expected_columns: List of expected column names.
    :return: DataFrame with the expected columns.
    """
    rows = []
    max_columns = len(expected_columns)

    with open(file_path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            try:
                # Parse the line into columns
                row = line.strip().split(",")
                if len(row) > max_columns:
                    # If the row has extra columns, truncate it
                    # print(
                    #     f"Truncating extra columns at line {line_number}: {line.strip()}"
                    # )
                    row = row[:max_columns]
                elif len(row) < max_columns:
                    # If the row has missing columns, pad with empty strings
                    print(
                        f"Padding missing columns at line {line_number}: {line.strip()}"
                    )
                    row.extend([""] * (max_columns - len(row)))
                rows.append(row)
            except Exception as e:
                print(f"Error processing row at line {line_number}: {e}")

    # Create a DataFrame from the collected rows
    df = pd.DataFrame(rows, columns=expected_columns)

    return df


def process_dataframes(dataframes):
    """
    Process and clean multiple DataFrames efficiently.
    :param dataframes: Dictionary where keys are DataFrame names and values are DataFrames.
    :return: Dictionary of cleaned DataFrames.
    """
    cleaned_dataframes = {}

    for name, df in dataframes.items():
        try:
            if name == "team_standings":
                # Clean the team standings DataFrame
                cleaned_dataframes[name] = clean_team_standings(df)
            elif name in ["hitters", "pitchers"]:
                # Clean hitters and pitchers DataFrames
                cleaned_dataframes[name] = (
                    clean_hitters(df) if name == "hitters" else clean_pitchers(df)
                )
            elif name in ["hitter_leaderboard", "pitcher_leaderboard"]:
                # Clean leaderboard DataFrames
                cleaned_dataframes[name] = clean_leaderboard(df)
            else:
                # If no specific cleaning function exists, keep the DataFrame as is
                cleaned_dataframes[name] = df
        except Exception as e:
            print(f"Error processing DataFrame '{name}': {e}")

    return cleaned_dataframes


def load_and_process_dataframes():
    """
    Load CSV files into DataFrames, process them, and return cleaned DataFrames.
    :return: Dictionary of cleaned DataFrames.
    """
    # Define the expected columns for each CSV file
    team_standings_columns = [
        "id",
        "year",
        "team_roster",
        "wins",
        "losses",
        "win_percentage",
        "games_behind",
    ]
    leaderboard_columns = ["id", "year", "statistic", "team", "value"]

    # Load the CSV files into DataFrames
    try:
        hitters_df = pd.read_csv(CSV_FILES["hitters"], on_bad_lines="skip")
    except Exception as e:
        print("Error loading hitters CSV:", e)
        hitters_df = pd.DataFrame()

    try:
        pitchers_df = pd.read_csv(CSV_FILES["pitchers"], on_bad_lines="skip")
    except Exception as e:
        print("Error loading pitchers CSV:", e)
        pitchers_df = pd.DataFrame()

    try:
        team_standings_df = load_csv_with_fallback(
            CSV_FILES["team_standings"], team_standings_columns
        )
    except Exception as e:
        print("Error loading team standings CSV:", e)
        team_standings_df = pd.DataFrame()

    try:
        hitter_leaderboard_df = load_csv_with_fallback(
            CSV_FILES["hitter_leaderboard"], leaderboard_columns
        )
    except Exception as e:
        print("Error loading hitter leaderboard CSV:", e)
        hitter_leaderboard_df = pd.DataFrame()

    try:
        pitcher_leaderboard_df = load_csv_with_fallback(
            CSV_FILES["pitcher_leaderboard"], leaderboard_columns
        )
    except Exception as e:
        print("Error loading pitcher leaderboard CSV:", e)
        pitcher_leaderboard_df = pd.DataFrame()

    # Combine the DataFrames into a dictionary
    dataframes = {
        "hitters": hitters_df,
        "pitchers": pitchers_df,
        "team_standings": team_standings_df,
        "hitter_leaderboard": hitter_leaderboard_df,
        "pitcher_leaderboard": pitcher_leaderboard_df,
    }

    # Process and clean the DataFrames
    cleaned_dataframes = process_dataframes(dataframes)

    return cleaned_dataframes


if __name__ == "__main__":
    # Load and process the DataFrames
    cleaned_dataframes = load_and_process_dataframes()

    # Save the cleaned DataFrames back to new CSV files
    cleaned_dataframes["hitters"].to_csv("hitters_data_cleaned.csv", index=False)
    cleaned_dataframes["pitchers"].to_csv("pitchers_data_cleaned.csv", index=False)
    cleaned_dataframes["team_standings"].to_csv(
        "team_standings_data_cleaned.csv", index=False
    )
    cleaned_dataframes["hitter_leaderboard"].to_csv(
        "hitter_leaderboard_data_cleaned.csv", index=False
    )
    cleaned_dataframes["pitcher_leaderboard"].to_csv(
        "pitcher_leaderboard_data_cleaned.csv", index=False
    )

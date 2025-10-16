## Baseball Scraper
## Consolidated Web Scraping Script for the American League

import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# URL for the website
website_url = "https://www.baseball-almanac.com/yearmenu.shtml"

# Header normalization map
header_map = {
    "Statistic": "statistic",
    "Name(s)": "name",
    "Team(s)": "team",
    "#": "value",
    "Top 25": "top_25",
    "Team | Roster": "team_roster",
    "W": "wins",
    "L": "losses",
    "WP": "win_percentage",
    "GB": "games_behind",
}

# CSV file mapping for different table types
CSV_FILES = {
    "hitters": "hitters_data.csv",
    "pitchers": "pitchers_data.csv",
    "team_standings": "team_standings_data.csv",
    "hitter_leaderboard": "hitter_leaderboard_data.csv",
    "pitcher_leaderboard": "pitcher_leaderboard_data.csv",
}


def pitcher_or_hitter(title, subtitle):
    if "team review" in title.lower():
        if "hitting" in subtitle.lower():
            return "hitting"
        elif "pitching" in subtitle.lower():
            return "pitching"
    return None


# Function to initialize the Selenium WebDriver
def initialize_driver():
    """Initialize the Selenium WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )
    return driver


# Function to find all year links for the American League
def get_american_league_year_links(driver):
    """Find all year links for the American League."""
    driver.get(website_url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
    )
    tables = driver.find_elements(By.CSS_SELECTOR, "table")
    american_league_table = tables[
        1
    ]  # The second table contains the American League links
    year_links = american_league_table.find_elements(By.TAG_NAME, "a")
    return [link.get_attribute("href") for link in year_links]


def get_data(wrapper):
    """Return types is a tuple of (hitters, pitchers, team_standings, pitcher_leaderboard, hitter_leaderboard) each are dicts with keys: title, subtitle, headers, rows"""
    containers = wrapper.find_elements(By.CSS_SELECTOR, "div.container")
    hitters = pitchers = team_standings = None
    pitcher_leaderboard = hitter_leaderboard = None
    table_index = 0

    for container in containers:
        table_divs = container.find_elements(By.CSS_SELECTOR, "div.ba-table")
        for div in table_divs:
            try:
                table = div.find_element(By.CSS_SELECTOR, "table.boxed")
                tbody = table.find_element(By.TAG_NAME, "tbody")
                rows = tbody.find_elements(By.TAG_NAME, "tr")

                if not rows or len(rows) < 3:
                    continue

                try:
                    title = rows[0].find_element(By.TAG_NAME, "h2").text.strip()
                    subtitle = rows[0].find_element(By.TAG_NAME, "p").text.strip()
                except:
                    title = rows[0].text.strip()
                    subtitle = ""

                data_rows = []
                previous_row_data = {}
                rowspan_tracker = {}
                headers = []
                current_division = None

                row_index = 1
                while row_index < len(rows) - 2:
                    row = rows[row_index]
                    cells = row.find_elements(By.TAG_NAME, "td")
                    cell_classes = [cell.get_attribute("class") or "" for cell in cells]

                    # Detect banner row with division
                    if any("banner" in cls for cls in cell_classes):
                        headers = []
                        current_division = None
                        for cell in cells:
                            cls = cell.get_attribute("class") or ""
                            text = cell.text.strip()
                            if "banner middle" in cls and cell.get_attribute("rowspan"):
                                if "east" in text.lower() or "west" in text.lower():
                                    current_division = text
                                    headers.append("Division")
                            elif "banner" in cls:
                                normalized = header_map.get(text, text)
                                headers.append(normalized)
                        row_index += 1
                        continue

                    # Parse data row
                    row_data = {}
                    cell_index = header_index = 0

                    while header_index < len(headers):
                        header = headers[header_index]

                        if header == "Division" and current_division:
                            row_data["Division"] = current_division
                            header_index += 1
                            continue

                        if (
                            header_index in rowspan_tracker
                            and rowspan_tracker[header_index]["remaining"] > 0
                        ):
                            row_data[header] = rowspan_tracker[header_index]["value"]
                            rowspan_tracker[header_index]["remaining"] -= 1
                            header_index += 1
                            continue

                        if cell_index >= len(cells):
                            row_data[header] = previous_row_data.get(header, "")
                            header_index += 1
                            continue

                        cell = cells[cell_index]
                        text = cell.text.strip()
                        rowspan = cell.get_attribute("rowspan")
                        if rowspan and rowspan.isdigit():
                            rowspan_tracker[header_index] = {
                                "value": text,
                                "remaining": int(rowspan) - 1,
                            }

                        row_data[header] = text
                        cell_index += 1
                        header_index += 1

                    previous_row_data = row_data.copy()
                    data_rows.append(row_data)
                    row_index += 1

                review_type = pitcher_or_hitter(title, subtitle)
                table_data = {
                    "title": title,
                    "subtitle": subtitle,
                    "headers": headers,
                    "rows": data_rows,
                }

                if review_type == "pitching":
                    pitcher_leaderboard = table_data
                elif review_type == "hitting":
                    hitter_leaderboard = table_data
                elif table_index == 0:
                    hitters = table_data
                elif table_index == 1:
                    pitchers = table_data
                elif (
                    table_index == 2
                    and "team standings" in title.lower() + subtitle.lower()
                ):
                    team_standings = table_data

                table_index += 1

            except Exception as e:
                print(f"Error parsing table {table_index}, {title}: {e}")
                continue

    return (
        hitters,
        pitchers,
        team_standings,
        pitcher_leaderboard,
        hitter_leaderboard,
    )


# Function to scrape a single year page
def scrape_year_page(driver, year_url, year):
    """Scrape data from a single year page. returns a dict with keys as table types and values as dictionaries with keys: headers, title, subtitle, rows."""
    driver.get(year_url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#wrapper"))
    )
    main = driver.find_element(By.CSS_SELECTOR, "body").find_element(
        By.CSS_SELECTOR, "#wrapper"
    )
    (
        hitters,
        pitchers,
        team_standings,
        pitcher_leaderboard,
        hitter_leaderboard,
    ) = get_data(main)

    return {
        "hitters": hitters,
        "pitchers": pitchers,
        "team_standings": team_standings,
        "pitcher_leaderboard": pitcher_leaderboard,
        "hitter_leaderboard": hitter_leaderboard,
    }


# Function to save data to CSV files
def save_data_to_csv(data, headers, csv_file, start_id=1, year=None):
    """
    Save data to a CSV file. Adds a unique ID and year to each row.
    :param data: List of dictionaries representing rows of data.
    :param headers: List of headers for the CSV file.
    :param csv_file: Path to the CSV file.
    :param start_id: Starting value for the unique ID.
    :param year: The year to add to each row.
    """
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
        # Add "id" and "year" to the headers for the unique identifier and year
        headers_with_id_and_year = ["id", "year"] + headers
        writer = csv.DictWriter(file, fieldnames=headers_with_id_and_year)

        if not file_exists:
            writer.writeheader()

        # Add a unique ID and year to each row and write to the file
        for i, row in enumerate(data, start=start_id):
            row_with_id_and_year = {"id": i, "year": year}  # Add unique ID and year
            row_with_id_and_year.update(row)
            writer.writerow(row_with_id_and_year)


# Function to scrape all years for the American League
def scrape_american_league():
    """
    Scrape data for all years in the American League.
    Saves data to CSV files with unique IDs and year for each row.
    """
    driver = initialize_driver()
    year_links = get_american_league_year_links(driver)
    row_counters = {
        key: 1 for key in CSV_FILES.keys()
    }  # Track unique IDs for each table type

    try:
        for i, year_url in enumerate(year_links):
            year = year_url.split("yr")[-1][:4]  # Extract the year from the URL
            print(f"Scraping data for year {year}...")
            year_table_data = scrape_year_page(driver, year_url, year)

            # Process and save data for each table type
            for table_type, table in year_table_data.items():
                if table is None or "rows" not in table or "headers" not in table:
                    print(f"Skipping invalid table for year {year}.")
                    continue  # Skip invalid tables

                # Save headers and rows to the corresponding CSV file
                save_data_to_csv(
                    data=table["rows"],
                    headers=table["headers"],
                    csv_file=CSV_FILES[table_type],
                    start_id=row_counters[table_type],
                    year=year,  # Pass the year to save in each row
                )

                # Update the row counter for the next batch
                row_counters[table_type] += len(table["rows"])

    finally:
        driver.quit()


# Main entry point
if __name__ == "__main__":
    scrape_american_league()

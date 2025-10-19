# Baseball Statistics Dashboard

This project is an interactive Baseball Statistics Dashboard that provides insights into historical baseball data. The dashboard allows users to explore team standings, hitter and pitcher leaderboards, and performance trends over time. The project covers the full data workflow; From data cleaning and processing to interactive visual analytics.

---

## Features

### 1. Interactive Dashboard
- Team Standings: View team wins, losses, and other metrics for a selected year.
- Hitter and Pitcher Leaderboards: Explore player statistics such as runs, home runs, strikeouts, and more.
- Performance Trends: Analyze trends over all years or within a 10-year range around a selected year.
- Dynamic Visualizations: Interactive charts and tables update instantly based on user input.

### 2. Data Cleaning and Processing
- Raw CSV data is cleaned and processed using Python scripts to ensure consistency and accuracy.
- Missing values are handled, and numeric columns are converted to the correct data types.

### 3. Lightweight and Easy to Use
- Built with Dash, the dashboard runs locally and is accessible via a web browser.
- No external database or complex setup is required.

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/linh-pham19/ScrapingProject.git
cd ScrapingProject/
```

### 2. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the Dashboard

```bash
python dashboard.py
```

Once the server starts, open your browser and navigate to `http://127.0.0.1:8050/` to access the dashboard.


---

## Dashboard Features

### Team Standings
- Displays team wins, losses, and other metrics for a selected year.
- Includes a bar chart visualizing wins and losses for each team.

### Hitter and Pitcher Leaderboards
- Interactive tables display player statistics such as runs, home runs, and strikeouts.
- Trend charts show performance changes over time, either for all years or within a 10-year range around the selected year.

### Dynamic Year Selection
- A dropdown menu allows users to select a specific year, and all tables and charts update dynamically.

---

## Data Cleaning

The `data_cleaner.py` script ensures the data is consistent and ready for visualization. Key steps include:
- **Column Normalization**: Ensures column names are consistent across datasets.
- **Missing Value Handling**: Drops rows with missing values in critical columns.
- **Data Type Conversion**: Converts numeric columns to the correct data types.

---

## Technologies Used

- **Python**: Core programming language.
- **Dash**: Framework for building interactive web applications.
- **Pandas**: Data manipulation and cleaning.
- **Plotly**: Interactive charting library.

---

## Example Insights

- **Home Run Leaders**: Analyze which players consistently led the league in home runs over the years.
- **Pitching Trends**: Explore how pitching performance evolved over time, including changes in ERA and strikeouts.
- **Team Performance**: Compare team standings and identify dominant teams in specific years.

---

## Future Improvements

- Add more advanced visualizations, such as heatmaps and scatter plots.
- Integrate real-time data updates for live statistics.
- Expand the dashboard to include additional metrics and filters.

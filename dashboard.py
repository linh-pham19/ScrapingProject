import dash
from dash import dcc, html, Input, Output
import pandas as pd
import data_cleaner

# Load and process the data
cleaned_dataframes = data_cleaner.load_and_process_dataframes()

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Baseball Data Dashboard"
server = app.server  # Expose the server variable for deployments

# Extract unique years from the team standings and leaderboard data
team_standings_df = cleaned_dataframes["team_standings"]
hitter_leaderboard_df = cleaned_dataframes["hitter_leaderboard"]
pitcher_leaderboard_df = cleaned_dataframes["pitcher_leaderboard"]

# Ensure the `year` column exists and is numeric
team_standings_df["year"] = pd.to_numeric(team_standings_df["year"], errors="coerce")
hitter_leaderboard_df["year"] = pd.to_numeric(
    hitter_leaderboard_df["year"], errors="coerce"
)
pitcher_leaderboard_df["year"] = pd.to_numeric(
    pitcher_leaderboard_df["year"], errors="coerce"
)

unique_years = sorted(team_standings_df["year"].dropna().unique())

# Define the layout of the app
app.layout = html.Div(
    children=[
        html.H1(
            "Baseball Data Dashboard",
            style={
                "textAlign": "center",
                "color": "white",
                "backgroundColor": "#6a0dad",
                "padding": "10px",
                "borderRadius": "10px",
            },
        ),
        # Dropdown for year selection
        html.Div(
            [
                html.Label("Select a Year:", style={"color": "#6a0dad"}),
                dcc.Dropdown(
                    id="year-dropdown",
                    options=[{"label": year, "value": year} for year in unique_years],
                    value=unique_years[0],  # Default to the first year
                    clearable=False,
                    style={"color": "#6a0dad"},
                ),
            ],
            style={
                "width": "50%",
                "margin": "0 auto 0.5rem",
                "pad1ing": "10px",
                "backgroundColor": "#e6e6fa",
                "borderRadius": "10px",
            },
        ),
        # Table to display team standings
        html.Div(
            id="team-standings-container",
            children=[
                html.H3(
                    "Team Standings",
                    style={"textAlign": "center", "color": "#6a0dad"},
                ),
                html.Div(id="team-standings-table"),
            ],
            style={"padding": "10px"},
        ),  # Chart to display wins and losses
        html.Div(
            id="chart-container",
            children=[
                html.H3(
                    "Team Standings Chart",
                    style={"textAlign": "center", "color": "#6a0dad"},
                ),
                dcc.Graph(id="wins-losses-chart"),
            ],
            style={"padding": "10px 30px"},
        ),
        # Table to display hitter leaderboard
        html.Div(
            id="hitter-leaderboard-container",
            children=[
                html.H3(
                    "Hitter Leaderboard",
                    style={"textAlign": "center", "color": "#6a0dad"},
                ),
                html.Div(id="hitter-leaderboard-table"),
                dcc.Graph(id="hitter-leaderboard-trend-chart"),
            ],
            style={"padding": "10px 30px"},
        ),
        # Table to display pitcher leaderboard
        html.Div(
            id="pitcher-leaderboard-container",
            children=[
                html.H3(
                    "Pitcher Leaderboard",
                    style={"textAlign": "center", "color": "#6a0dad"},
                ),
                html.Div(id="pitcher-leaderboard-table"),
                dcc.Graph(id="pitcher-leaderboard-chart"),
            ],
            style={"padding": "10px 30px"},
        ),
    ],
    style={"backgroundColor": "#f8f0ff", "fontFamily": "Arial, sans-serif"},
)


# Helper function to generate an HTML table
def generate_table(dataframe):
    if dataframe.empty:
        return html.P("No data available for the selected year.")

    return html.Table(
        # Table header
        [
            html.Tr(
                [
                    html.Th(
                        col, style={"padding": "10px", "border": "1px solid #6a0dad"}
                    )
                    for col in dataframe.columns
                ]
            )
        ]
        +
        # Table rows
        [
            html.Tr(
                [
                    html.Td(
                        row[col],
                        style={"padding": "10px", "border": "1px solid #6a0dad"},
                    )
                    for col in dataframe.columns
                ]
            )
            for _, row in dataframe.iterrows()
        ],
        style={
            "width": "100%",
            "borderCollapse": "collapse",
            "margin": "0 auto 1rem",
            "color": "#6a0dad",
            "backgroundColor": "#f8f0ff",
        },
    )


# Callback to update the team standings table based on the selected year
@app.callback(
    Output("team-standings-table", "children"),
    Input("year-dropdown", "value"),
)
def update_team_standings_table(selected_year):
    filtered_df = team_standings_df[team_standings_df["year"] == selected_year]

    # Debugging
    print(f"Team Standings Data for Year {selected_year}:")
    print(filtered_df)

    if filtered_df.empty:
        return html.P("No data available for the selected year.")

    return generate_table(filtered_df)


# Callback to update the hitter leaderboard table and trend chart based on the selected year
@app.callback(
    [
        Output("hitter-leaderboard-table", "children"),
        Output("hitter-leaderboard-trend-chart", "figure"),
    ],
    Input("year-dropdown", "value"),
)
def update_hitter_leaderboard(selected_year):
    # Filter the DataFrame for the selected year
    filtered_df = hitter_leaderboard_df[hitter_leaderboard_df["year"] == selected_year]

    # Debugging
    print(f"Hitter Leaderboard Data for Year {selected_year}:")
    print(filtered_df)

    if filtered_df.empty:
        return html.P("No data available for the selected year."), {
            "data": [],
            "layout": {"title": "No data available for the selected year"},
        }

    # Determine the range of years for the trend chart
    min_year = max(hitter_leaderboard_df["year"].min(), selected_year - 5)
    max_year = min(hitter_leaderboard_df["year"].max(), selected_year + 5)
    trend_df = hitter_leaderboard_df[
        (hitter_leaderboard_df["year"] >= min_year)
        & (hitter_leaderboard_df["year"] <= max_year)
    ]

    # Generate a trend chart for hitter leaderboard
    trend_chart = {
        "data": [
            {
                "x": trend_df[trend_df["statistic"] == stat]["year"],
                "y": trend_df[trend_df["statistic"] == stat]["value"],
                "type": "scatter",
                "mode": "lines+markers",
                "name": stat,
            }
            for stat in trend_df["statistic"].unique()
        ],
        "layout": {
            "title": f"Hitter Leaderboard Trend ({min_year}-{max_year})",
            "xaxis": {"title": "Year"},
            "yaxis": {"title": "Value"},
        },
    }

    return generate_table(filtered_df), trend_chart


# Callback to update the pitcher leaderboard table and chart based on the selected year
@app.callback(
    [
        Output("pitcher-leaderboard-table", "children"),
        Output("pitcher-leaderboard-chart", "figure"),
    ],
    Input("year-dropdown", "value"),
)
def update_pitcher_leaderboard(selected_year):
    filtered_df = pitcher_leaderboard_df[
        pitcher_leaderboard_df["year"] == selected_year
    ]

    # Debugging
    print(f"Pitcher Leaderboard Data for Year {selected_year}:")
    print(filtered_df)

    if filtered_df.empty:
        return html.P("No data available for the selected year."), {
            "data": [],
            "layout": {"title": "No data available for the selected year"},
        }

    # Generate a line chart for pitcher leaderboard
    line_chart = {
        "data": [
            {
                "x": filtered_df["statistic"],
                "y": filtered_df["value"],
                "type": "scatter",
                "mode": "lines+markers",
                "name": "Pitcher Stats",
                "line": {"color": "#6a0dad"},
            }
        ],
        "layout": {
            "title": f"Pitcher Leaderboard for {selected_year}",
            "xaxis": {"title": "Statistic"},
            "yaxis": {"title": "Value"},
        },
    }

    return generate_table(filtered_df), line_chart


# Callback to update the wins and losses chart based on the selected year
@app.callback(
    Output("wins-losses-chart", "figure"),
    Input("year-dropdown", "value"),
)
def update_wins_losses_chart(selected_year):
    filtered_df = team_standings_df[team_standings_df["year"] == selected_year]

    # Debugging
    print(f"Wins and Losses Data for Year {selected_year}:")
    print(filtered_df)

    if filtered_df.empty:
        return {
            "data": [],
            "layout": {
                "title": "No data available for the selected year",
                "xaxis": {"title": "Teams"},
                "yaxis": {"title": "Wins/Losses"},
            },
        }

    figure = {
        "data": [
            {
                "x": filtered_df["team_roster"],
                "y": filtered_df["wins"],
                "type": "bar",
                "name": "Wins",
                "marker": {"color": "#6a0dad"},
            },
            {
                "x": filtered_df["team_roster"],
                "y": filtered_df["losses"],
                "type": "bar",
                "name": "Losses",
                "marker": {"color": "#e6e6fa"},
            },
        ],
        "layout": {
            "title": f"Wins and Losses for {selected_year}",
            "xaxis": {"title": "Teams"},
            "yaxis": {"title": "Wins/Losses"},
            "barmode": "group",
        },
    }

    return figure


if __name__ == "__main__":
    app.run(debug=True)

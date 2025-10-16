import dash
from dash import dcc, html, Input, Output
import pandas as pd
import data_cleaner

# Load and process the data
cleaned_dataframes = data_cleaner.load_and_process_dataframes()

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Sports Data Dashboard"
server = app.server  # Expose the server variable for deployments

# Extract unique years from the team standings data
team_standings_df = cleaned_dataframes["team_standings"]
hitters_df = cleaned_dataframes["hitters"]
pitchers_df = cleaned_dataframes["pitchers"]

# Ensure the `year` column exists and is numeric
if "year" not in hitters_df.columns:
    hitters_df["year"] = None
if "year" not in pitchers_df.columns:
    pitchers_df["year"] = None

# Strip any whitespace and ensure proper numeric conversion
hitters_df["year"] = hitters_df["year"].astype(str).str.strip()  # Remove extra spaces
pitchers_df["year"] = pitchers_df["year"].astype(str).str.strip()

# Convert to numeric, coercing errors to NaN
hitters_df["year"] = pd.to_numeric(hitters_df["year"], errors="coerce")
pitchers_df["year"] = pd.to_numeric(pitchers_df["year"], errors="coerce")

unique_years = sorted(team_standings_df["year"].unique())

# Define the layout of the app
app.layout = html.Div(
    children=[
        html.H1(
            "Sports Data Dashboard",
            style={
                "textAlign": "center",
                "color": "white",
                "backgroundColor": "#6a0dad",
                "padding": "20px",
                "borderRadius": "10px",
            },
        ),
        # Dropdown for year selection
        html.Div(
            [
                html.Label("Select a Year:", style={"color": "#e6e6fa"}),
                dcc.Dropdown(
                    id="year-dropdown",
                    options=[{"label": year, "value": year} for year in unique_years],
                    value=unique_years[0],  # Default to the first year
                    clearable=False,
                    style={"color": "black"},
                ),
            ],
            style={
                "width": "50%",
                "margin": "0 auto",
                "padding": "20px",
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
            style={"padding": "20px"},
        ),
        # Table to display hitters
        html.Div(
            id="hitters-container",
            children=[
                html.H3(
                    "Hitters Data",
                    style={"textAlign": "center", "color": "#6a0dad"},
                ),
                html.Div(id="hitters-table"),
            ],
            style={"padding": "20px"},
        ),
        # Table to display pitchers
        html.Div(
            id="pitchers-container",
            children=[
                html.H3(
                    "Pitchers Data",
                    style={"textAlign": "center", "color": "#6a0dad"},
                ),
                html.Div(id="pitchers-table"),
            ],
            style={"padding": "20px"},
        ),
        # Chart to display wins and losses
        html.Div(
            id="chart-container",
            children=[
                html.H3(
                    "Wins and Losses Chart",
                    style={"textAlign": "center", "color": "#6a0dad"},
                ),
                dcc.Graph(id="wins-losses-chart"),
            ],
            style={"padding": "20px"},
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
            "margin": "0 auto",
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

    # Check if the filtered DataFrame is empty
    if filtered_df.empty:
        return html.P("No data available for the selected year.")

    return generate_table(filtered_df)


# Callback to update the hitters table based on the selected year
@app.callback(
    Output("hitters-table", "children"),
    Input("year-dropdown", "value"),
)
def update_hitters_table(selected_year):
    filtered_df = hitters_df[hitters_df["year"] == selected_year]

    # Check if the filtered DataFrame is empty
    if filtered_df.empty:
        return html.P("No data available for the selected year.")

    return generate_table(filtered_df)


# Callback to update the pitchers table based on the selected year
@app.callback(
    Output("pitchers-table", "children"),
    Input("year-dropdown", "value"),
)
def update_pitchers_table(selected_year):
    filtered_df = pitchers_df[pitchers_df["year"] == selected_year]

    # Check if the filtered DataFrame is empty
    if filtered_df.empty:
        return html.P("No data available for the selected year.")

    return generate_table(filtered_df)


# Callback to update the wins and losses chart based on the selected year
@app.callback(
    Output("wins-losses-chart", "figure"),
    Input("year-dropdown", "value"),
)
def update_wins_losses_chart(selected_year):
    filtered_df = team_standings_df[team_standings_df["year"] == selected_year]

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


# Run the app
if __name__ == "__main__":
    app.run(debug=True)

#!/usr/bin/env python
# coding: utf-8

# In[ ]:

# import required libraries
import dash
import more_itertools  # (unused but kept to preserve your structure)
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

# Load the data using pandas
data = pd.read_csv(
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv"
)

# Initialize the Dash app
# app = dash.Dash(__name__)
# Dash app + WSGI server
app = dash.Dash(__name__)
server = app.server  # <-- WSGI callable for Waitress/Gunicorn/etc.

# Set the title of the dashboard
# app.title = "Automobile Statistics Dashboard"

# ---------------------------------------------------------------------------------
# Create the dropdown menu options
dropdown_options = [
    {"label": "Yearly Statistics report", "value": "Yearly Statistics"},
    {"label": "Recession Period Statistics", "value": "Recession Period Statistics"},
]
# List of years (built from data to avoid invalid defaults)
year_list = sorted(data["Year"].dropna().unique().tolist())
# ---------------------------------------------------------------------------------------
# Create the layout of the app
app.layout = html.Div(
    [
        # TASK 2.1 Add title to the dashboard
        html.H1(
            "Automobile Sales Statistics Dashboard",
            style={"textAlign": "center", "color": "#503D36", "fontSize": 24},
        ),  # Include style for title
        # TASK 2.2: Add two dropdown menus
        html.Div(
            [
                html.Label("Select Statistics:"),
                dcc.Dropdown(
                    id="dropdown-statistics",
                    options=[
                        {"label": "Yearly Statistics", "value": "Yearly Statistics"},
                        {"label": "Recession Period Statistics", "value": "Recession Period Statistics"},
                    ],
                    value='Recession Period Statistics',
                    placeholder="Select a report type",
                    style={
                        "width": "80%",
                        "padding": "3px",
                        "fontSize": "20px",
                        "textAlignLast": "center"
                    }
                )
            ]
        ),
        html.Div(
            dcc.Dropdown(
                id="select-year",
                options=[{"label": int(i), "value": int(i)} for i in year_list],
                value='Select-year',
                placeholder="Select-year",
                style={
                        "width": "80%",
                        "padding": "3px",
                        "fontSize": "20px",
                        "textAlignLast": "center"
                    }
            )
        ),
        html.Div([# TASK 2.3: Add a division for output display
                html.Div(
                    id="output-container",
                    className="chart-grid",
                    style={"display": "grid",
                           "gridTemplateColumns": "1fr 1fr",
                           "gap": "5x",
                           "width": "90%"},),
            ]),
    ]
)

# TASK 2.4: Creating Callbacks
# Define the callback function to update the input container based on the selected statistics
@app.callback(
    Output(component_id="select-year", component_property="disabled"),
    Input(component_id="dropdown-statistics", component_property="value"),
)
def update_input_container(selected_statistics):
    # Enable year dropdown ONLY for Yearly Statistics
    return False if selected_statistics == "Yearly Statistics" else True


# Callback for plotting
# Define the callback function to update the input container based on the selected statistics
@app.callback(
    Output(component_id="output-container", component_property="children"),
    [
        Input(component_id="dropdown-statistics", component_property="value"),
        Input(component_id="select-year", component_property="value"),
    ],
)
def update_output_container(report_type, selected_year):
    if report_type == "Recession Period Statistics":
        # Filter the data for recession periods
        recession_data = data[data["Recession"] == 1]

        # TASK 2.5: Create and display graphs for Recession Report Statistics

        # Plot 1 Automobile sales fluctuate over Recession Period (year wise)
        yearly_rec = (
            recession_data.groupby("Year")["Automobile_Sales"].mean().reset_index()
        )
        R_chart1 = dcc.Graph(
            figure=px.line(
                yearly_rec,
                x="Year",
                y="Automobile_Sales",
                title="Average Automobile Sales fluctuation over Recession Period",
            ),
            style={"width": "75%"}
        )

        # Plot 2 Calculate the average number of vehicles sold by vehicle type
        average_sales = (
            recession_data.groupby("Vehicle_Type")["Automobile_Sales"].mean().reset_index()
        )
        R_chart2 = dcc.Graph(
            figure=px.bar(
                average_sales,
                x="Vehicle_Type",
                y="Automobile_Sales",
                title="Average Vehicle Sales by Type During Recession",
            ),
            style={"width": "75%"}
        )

        # Plot 3 Pie chart for total expenditure share by vehicle type during recessions
        exp_rec = (
            recession_data.groupby("Vehicle_Type")["Advertising_Expenditure"]
            .sum()
            .reset_index()
        )
        R_chart3 = dcc.Graph(
            figure=px.pie(
                exp_rec,
                values="Advertising_Expenditure",
                names="Vehicle_Type",
                title="Advertising Expenditure Shares by Vehicle Type During Recession",
            ),
            style={"width": "75%"}
        )

        # Plot 4 bar chart for the effect of unemployment rate on vehicle type and sales
        unemp_data = (
            recession_data.groupby(["unemployment_rate", "Vehicle_Type"])[
                "Automobile_Sales"
            ]
            .mean()
            .reset_index()
        )
        R_chart4 = dcc.Graph(
            figure=px.bar(
                unemp_data,
                x="unemployment_rate",
                y="Automobile_Sales",
                color="Vehicle_Type",
                labels={
                    "unemployment_rate": "Unemployment Rate",
                    "Automobile_Sales": "Average Automobile Sales",
                },
                title="Effect of Unemployment Rate on Vehicle Type and Sales",
            ),
            style={"width": "75%"}
        )

        #return [
        #    html.Div(
        #        className="chart-item",
        #        children=[html.Div(children=R_chart1), html.Div(children=R_chart2)],
        #        style={"display": "flex"},
        #    ),
        #    html.Div(
        #        className="chart-item",
        #        children=[html.Div(children=R_chart3), html.Div(children=R_chart4)],
        #        style={"display": "flex"},
        #    ),
        #]
        return [R_chart1, R_chart2, R_chart3, R_chart4]

    # TASK 2.6: Create and display graphs for Yearly Report Statistics
    # Yearly Statistic Report Plots
    # Check for Yearly Statistics.
    elif report_type == "Yearly Statistics" and selected_year:
        yearly_data = data[data["Year"] == selected_year]

        # plot 1 Yearly Automobile sales using line chart for the whole period.
        yas = data.groupby("Year")["Automobile_Sales"].mean().reset_index()
        Y_chart1 = dcc.Graph(
            figure=px.line(
                yas, x="Year", y="Automobile_Sales", title="Yearly Average Automobile Sales"
            ),
            style={"width": "75%"}
        )

        # Plot 2 Total Monthly Automobile sales using line chart.
        mas = data.groupby("Month")["Automobile_Sales"].sum().reset_index()
        Y_chart2 = dcc.Graph(
            figure=px.line(
                mas, x="Month", y="Automobile_Sales", title="Total Monthly Automobile Sales"
            ),
            style={"width": "75%"}
        )

        # Plot 3: Average number of vehicles sold during the given year
        avr_vdata = (
            yearly_data.groupby("Vehicle_Type")["Automobile_Sales"].mean().reset_index()
        )
        Y_chart3 = dcc.Graph(
            figure=px.bar(
                avr_vdata,
                x="Vehicle_Type",
                y="Automobile_Sales",
                title=f"Average Vehicles Sold by Vehicle Type in the year {selected_year}",
            ),
            style={"width": "75%"}
        )

        # Plot 4: Total Advertisement Expenditure for each vehicle using pie chart
        exp_data = (
            yearly_data.groupby("Vehicle_Type")["Advertising_Expenditure"]
            .sum()
            .reset_index()
        )
        Y_chart4 = dcc.Graph(
            figure=px.pie(
                exp_data,
                values="Advertising_Expenditure",
                names="Vehicle_Type",
                title="Total Advertisement Expenditure for Each Vehicle",
            ),
            style={"width": "75%"}
        )

        # TASK 2.6: Returning the graphs for displaying Yearly data

        #return [
        #    html.Div(
        #        className="chart-item",
        #        children=[html.Div(children=Y_chart1), html.Div(children=Y_chart2)],
        #        style={"display": "flex"},
        #    ),
        #    html.Div(
        #        className="chart-item",
        #        children=[html.Div(children=Y_chart3), html.Div(children=Y_chart4)],
        #        style={"display": "flex"},
        #    ),
        #]
        return [Y_chart1, Y_chart2, Y_chart3, Y_chart4]

    # Default prompt
    return html.Div("Select a report type (and a year for Yearly Statistics).")


# Run the Dash app
if __name__ == "__main__":
    app.run(debug=True)

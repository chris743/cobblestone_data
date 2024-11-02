import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import numpy as np

# Database connection setup
DATABASE_TYPE = 'postgresql'
DBAPI = 'psycopg2'
USER = 'chrism'
PASSWORD = '!Cncamrts1'
HOST = '192.168.128.30'
PORT = '5432'
DATABASE = 'Production_data'
SCHEMA = 'production'
TABLE_NAME = 'orders'

engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

dash.register_page(__name__, path='/bin_inventory')

DARK_BG_COLOR = "#1e1e1e"
TEXT_COLOR = "white"

# Layout for orders page
layout = html.Div([
    html.Div([
        # Pie chart for Commodity Distribution
        dcc.Graph(id='bin-commodity-pie-chart', style={'width': '25%', 'height': '40vh', 'display': 'inline-block'}),

        # Bar charts for Size Distribution per Commodity
        html.Div(
            id='bin-size-bar-charts',
            style={'width': '75%', 'display': 'inline-block', 'flex-wrap': 'wrap'}
        ),
        
        # Bar charts for Room Row Location
        html.Div([
            dcc.Graph(id=f'room-row-location-bar-chart-{i}', style={'width': '45%', 'display': 'inline-block', 'height': '30vh'})
            for i in range(1, 5)
        ], style={'display': 'flex', 'flex-wrap': 'wrap'})
    ], style={'display': 'flex'}),
    dcc.Interval(id='interval-component', interval=5*60*1000, n_intervals=0)  # 5-minute update interval
], style={'backgroundColor': DARK_BG_COLOR, 'padding': '10px'})

# Function to apply dark mode theme to figures
def dark_mode_fig(fig):
    fig.update_layout(
        paper_bgcolor=DARK_BG_COLOR,
        plot_bgcolor=DARK_BG_COLOR,
        font=dict(color=TEXT_COLOR),
        xaxis=dict(gridcolor='#444'),
        yaxis=dict(gridcolor='#444')
    )
    return fig

# Callback for updating charts and metrics
@dash.callback(
    [Output('bin-commodity-pie-chart', 'figure')] +
    [Output(f'room-row-location-bar-chart-{i}', 'figure') for i in range(1, 5)],
    Input('interval-component', 'n_intervals')
)
def update_charts_and_cards(n_intervals):
    with engine.connect() as connection:
        # Query data from PostgreSQL
        query = f"SELECT commodity_id, on_hand_quantity, room_row_location FROM {SCHEMA}.{TABLE_NAME}"
        df = pd.read_sql(query, connection)

    # Pie chart for Commodity Distribution (Sum of on_hand_quantity)
    bin_commodity_sum = df.groupby('commodity_id')['on_hand_quantity'].sum().reset_index()
    bin_commodity_pie_fig = px.pie(bin_commodity_sum, values='on_hand_quantity', names='commodity_id',
                                   title="Commodity Distribution")
    bin_commodity_pie_fig = dark_mode_fig(bin_commodity_pie_fig)

    # Prepare data for Room Row Location bar charts
    room_row_location_counts = df['room_row_location'].value_counts().reset_index()
    room_row_location_counts.columns = ['room_row_location', 'bin_count']

    # Split the data into four parts for the four bar charts
    bar_chart_figures = []
    split_data = np.array_split(room_row_location_counts, 4)  # Split data for four bar charts
    for i, data_chunk in enumerate(split_data, 1):
        bar_chart_fig = px.bar(data_chunk, x='room_row_location', y='bin_count',
                               title=f"Room Row Location - Part {i}")
        bar_chart_fig = dark_mode_fig(bar_chart_fig)
        bar_chart_figures.append(bar_chart_fig)

    return (bin_commodity_pie_fig, *bar_chart_figures)

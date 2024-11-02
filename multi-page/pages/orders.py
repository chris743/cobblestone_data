import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from datetime import date


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

dash.register_page(__name__, path='/orders')  # Register page

DARK_BG_COLOR = "#1e1e1e"
TEXT_COLOR = "white"

# Database connection setup
DATABASE_URL = "postgresql://chrism:!Cncamrts1@192.168.128.30:5432/Production_data"
engine = create_engine(DATABASE_URL)

# Layout for orders page
layout = html.Div([
    #html.H1("Sales Order Data Dashboard", style={'color': TEXT_COLOR}),

    dcc.Interval(
        id='interval-component',
        interval=100*1000,  # Update every 10 seconds
        n_intervals=0  # Initialize the number of intervals
    ),

    html.Div([
        # Pie chart for Commodity Distribution
        dcc.Graph(id='commodity-pie-chart', style={'width': '25%', 'height': '40vh', 'display': 'inline-block'}),

        # Bar charts for Size Distribution per Commodity
        html.Div(
            id='size-bar-charts',
            style={'width': '75%', 'display': 'inline-block', 'flex-wrap': 'wrap'}
        )
    ], style={'display': 'flex'}),

    # Line chart for Total Order Quantity per Day
    dcc.Graph(id='order-quantity-line-chart', style={'height': '35vh'}),

    # Four cards at the bottom with key metrics
    html.Div([
        dbc.Card([
            dbc.CardBody([
                html.H5("Total Quantity Shipping", className="card-title"),
                html.P(id='total-shipping-today', className="card-text"),
                html.P(id='total-shipping-season', className="card-text"),
            ])
        ], color="secondary", inverse=True, style={'backgroundColor': DARK_BG_COLOR}),

        dbc.Card([
            dbc.CardBody([
                html.H5("Volume of day-of Orders", className="card-title"),
                html.P(id='total-day-of', className="card-text"),
            ])
        ], color="secondary", inverse=True, style={'backgroundColor': DARK_BG_COLOR}),

        dbc.Card([
            dbc.CardBody([
                html.H5("Volume assigned today", className="card-title"),
                html.P(id='total-assigned-day-of', className="card-text"),
            ])
        ], color="secondary", inverse=True, style={'backgroundColor': DARK_BG_COLOR}),

        dbc.Card([
            dbc.CardBody([
                html.H5("Total Bag and Bulk Business", className="card-title"),
                html.P(id='total-bag', className="card-text", children="Bag: TBD"),
                html.P(id='total-bulk', className="card-text", children="Bulk: TBD")
            ])
        ], color="secondary", inverse=True, style={'backgroundColor': DARK_BG_COLOR}),

                dbc.Card([
            dbc.CardBody([
                html.H5("Average Line Quantity", className="card-title"),
                html.P(id='avg-line-qty', className="card-text"),
            ])
        ], color="secondary", inverse=True, style={'backgroundColor': DARK_BG_COLOR}),

                dbc.Card([
            dbc.CardBody([
                html.H5("Average Order Quantity", className="card-title"),
                html.P(id='avg-order-qty', className="card-text"),
            ])
        ], color="secondary", inverse=True, style={'backgroundColor': DARK_BG_COLOR}),

                dbc.Card([
            dbc.CardBody([
                html.H5("Total Export Sales", className="card-title"),
                html.P(id='total-export-sales', className="card-text"),
            ])
        ], color="secondary", inverse=True, style={'backgroundColor': DARK_BG_COLOR}),

                        dbc.Card([
            dbc.CardBody([
                html.H5("Largest Single Day", className="card-title"),
                html.P(id='largest-single-day', className="card-text"),
            ])
        ], color="secondary", inverse=True, style={'backgroundColor': DARK_BG_COLOR}),

    ], style={'display': 'flex', 'justify-content': 'space-between', 'margin-top': '20px', 'width': '100%', 'padding-left': '2rem', 'padding-right': '2rem'}),
], style={'backgroundColor': DARK_BG_COLOR, 'padding': '10px'})  # Set the main layout background color

# Function to apply dark mode theme to figures
def dark_mode_fig(fig):
    fig.update_layout(
        paper_bgcolor=DARK_BG_COLOR,  # Background for figure
        plot_bgcolor=DARK_BG_COLOR,   # Background for plot area
        font=dict(color=TEXT_COLOR),  # Color of text
        xaxis=dict(gridcolor='#444'),  # Gridline color
        yaxis=dict(gridcolor='#444')   # Gridline color
    )
    return fig

# Callbacks for updating charts and metrics
@dash.callback(
    Output('commodity-pie-chart', 'figure'),
    Output('size-bar-charts', 'children'),
    Output('order-quantity-line-chart', 'figure'),
    Output('total-shipping-today', 'children'),
    Output('total-shipping-season', 'children'),
    Output('total-day-of', 'children'),
    Output('total-assigned-day-of', 'children'),
    Output('total-bag', 'children'),
    Output('total-bulk', 'children'),
    Output('avg-order-qty', 'children'),
    Output('avg-line-qty', 'children'),
    Output('total-export-sales', 'children'),
    Output('largest-single-day', 'children'),
    Input('interval-component', 'n_intervals'),  # Trigger callback on interval
)
def update_charts_and_cards(n_intervals):
    # Load data into a DataFrame
    with engine.connect() as connection:
        #query = f"SELECT commodity_id, size_id, style_id, order_quantity, ship_date, flag, salesperson FROM {SCHEMA}.{TABLE_NAME}"
        query = f"SELECT * FROM {SCHEMA}.{TABLE_NAME}"

        df = pd.read_sql(query, connection)

    # Convert ship_date to datetime
    df['ship_date'] = pd.to_datetime(df['ship_date'])

    # Apply multiplication for tri-wall or TWB styles
    df['order_quantity'] = df.apply(
        lambda row: row['order_quantity'] * 18 if row['style_id'] and ('tri-wall' in row['style_id'].lower() or 'twb' in row['style_id'].lower()) else row['order_quantity'],
        axis=1
    )

    # Filter data based on selected date range for pie and bar charts
    today = date.today()
    filtered_df = df[df['ship_date'] == pd.Timestamp(today)]

    # Pie chart for Commodity Distribution (Sum of Order Quantity)
    commodity_sum = filtered_df.groupby('commodity_id')['order_quantity'].sum()
    commodity_pie_fig = px.pie(commodity_sum, values=commodity_sum.values, names=commodity_sum.index,
                               title="Commodity Distribution")
    commodity_pie_fig = dark_mode_fig(commodity_pie_fig)

    # Bar charts for Size Distribution per Commodity (Sum of Order Quantity)
    size_bar_charts = []
    for commodity in filtered_df['commodity_id'].unique():
        commodity_data = filtered_df[filtered_df['commodity_id'] == commodity]
        size_sum = commodity_data.groupby('size_id')['order_quantity'].sum()

        fig = px.bar(size_sum, x=size_sum.index, y=size_sum.values,
                     labels={'x': '', 'y': 'Total Order Quantity'},
                     title=f"Size Distribution for {commodity}",
                     text=size_sum.values)

        fig.update_traces(texttemplate='%{text}', textposition='inside')
        fig = dark_mode_fig(fig)

        size_bar_charts.append(dcc.Graph(figure=fig, style={'width': '25%', 'height': '24vh', 'display': 'inline-block'}))

    # Line chart for Total Order Quantity per Day (using all dates)
    daily_order_quantity = df.groupby('ship_date')['order_quantity'].sum().reset_index()
    order_quantity_line_fig = px.line(daily_order_quantity, x='ship_date', y='order_quantity',
                                      labels={'ship_date': 'Date', 'order_quantity': 'Total Order Quantity'},
                                      title="Total Order Quantity Over Time")
    order_quantity_line_fig = dark_mode_fig(order_quantity_line_fig)

    # Metrics for the cards
    total_shipping_today = filtered_df['order_quantity'].sum()
    total_shipping_season = df['order_quantity'].sum()
    total_day_of = filtered_df[filtered_df['flag'] == 'day_of_order']['order_quantity'].sum()
    total_assigned_day_of = filtered_df[filtered_df['flag'].isin(['assigned_day_of', 'day_of_order'])]['order_quantity'].sum()

    # Calculate total bags and total bulk
    total_bags = filtered_df[filtered_df['style_id'].str.contains("giro|fox|vex|TWB", case=False, na=False)]['order_quantity'].sum()
    total_bulk = total_shipping_today - total_bags

    avg_order_qty = df.groupby("sales_order_number")['order_quantity'].mean().mean()
    avg_order_qty=round(avg_order_qty)

    avg_line_qty = filtered_df['order_quantity'].mean()
    avg_line_qty = round(avg_line_qty)

    total_export_sales = df[df['salesperson'].str.contains("JIM LAMB", case=False, na=False)]['order_quantity'].sum()

    largest_single_day = df.groupby("ship_date")['order_quantity'].sum().max()

    
    return (
        commodity_pie_fig,
        size_bar_charts,
        order_quantity_line_fig,
        f"TODAY: {total_shipping_today:,}",
        f"SEASON: {total_shipping_season:,}",
        f"TODAY: {total_day_of:,}",
        f"TODAY: {total_assigned_day_of:,}",
        f"BAGS: {total_bags:,}",
        f"BULK: {total_bulk:,}",
        f"TODAY: {avg_order_qty:,}",
        f"TODAY: {avg_line_qty:,}",
        f"TODAY: {total_export_sales:,}",
        f"{largest_single_day:,}",
    )

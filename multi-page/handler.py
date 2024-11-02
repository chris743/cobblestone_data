from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import dash

app = Dash(__name__,  external_stylesheets=[dbc.themes.DARKLY], use_pages=True)
app.layout = html.Div([
    dbc.NavbarSimple(
        children=[
            dbc.NavLink("Orders", href="/orders", active="exact"),
            dbc.NavLink("Bin Inventory", href="/bin_inventory", active="exact"),
        ],
        brand="Dashboard",
        color="primary",
        dark=True,
    ),
    dcc.Location(id="url"),
    dash.page_container  # Renders the appropriate page content
])

if __name__ == '__main__':
    app.run_server(debug=True)

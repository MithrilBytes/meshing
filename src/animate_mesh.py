# src/animate_mesh.py
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import requests
from skyfield.api import load, EarthSatellite
import numpy as np

# Configuration
TIME_STEP = 10  # Update interval in seconds
MAX_SATELLITES = 300  # Increase satellite limit for more coverage
DISTANCE_THRESHOLD = 1500  # km for mesh connection

# Load timescale for Skyfield
ts = load.timescale()

# Fetch real-time satellite data from CelesTrak
def fetch_satellites():
    tle_url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"

    try:
        response = requests.get(tle_url)
        response.raise_for_status()

        # Ensure the response contains TLE data and not an HTML error page
        if "<html" in response.text.lower():
            print("Error: Received HTML instead of TLE data. CelesTrak might be down.")
            return []

        tle_lines = response.text.strip().split("\n")
        satellites = []

        for i in range(0, len(tle_lines), 3):
            try:
                name = tle_lines[i].strip() or f"Unnamed Satellite {i//3 + 1}"
                line1 = tle_lines[i + 1].strip()
                line2 = tle_lines[i + 2].strip()

                # Validate line length to avoid malformed TLEs
                if len(line1) != 69 or len(line2) != 69:
                    print(f"Skipping malformed TLE for {name}")
                    continue

                # Create satellite object
                satellite = EarthSatellite(line1, line2, name, ts)
                satellites.append(satellite)

            except Exception as e:
                print(f"Failed to parse TLE lines {i}–{i+2}: {e}")
                continue

            if len(satellites) >= MAX_SATELLITES:
                break

        print(f"Successfully loaded {len(satellites)} satellites.")
        return satellites

    except requests.exceptions.RequestException as e:
        print(f"Error fetching TLE data: {e}")
        return []

# Get current positions of satellites
def get_satellite_positions():
    satellites = fetch_satellites()
    now = ts.now()

    positions = []
    for sat in satellites:
        try:
            geocentric = sat.at(now)
            subpoint = geocentric.subpoint()
            positions.append({
                'name': sat.name,
                'lat': subpoint.latitude.degrees,
                'lon': subpoint.longitude.degrees,
                'alt': subpoint.elevation.km
            })
        except Exception as e:
            print(f"Failed to calculate position for {sat.name}: {e}")
            continue

    return positions

# Dash app setup
app = dash.Dash(__name__)
app.title = "Real-Time Satellite Mesh Network"

# Layout
app.layout = html.Div([
    html.H1("Real-Time Satellite Mesh Network", style={'textAlign': 'center'}),
    dcc.Graph(id='satellite-graph'),
    dcc.Interval(id='interval-component', interval=TIME_STEP * 1000, n_intervals=0)
])

# Update graph callback
@app.callback(
    Output('satellite-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graph(n):
    satellites = get_satellite_positions()

    # Create figure
    fig = go.Figure()

    # Add satellite markers
    lats, lons, alts, names = [], [], [], []
    for sat in satellites:
        lats.append(sat['lat'])
        lons.append(sat['lon'])
        alts.append(sat['alt'])
        names.append(sat['name'])

    fig.add_trace(go.Scattergeo(
        lon=lons,
        lat=lats,
        mode='markers',
        marker=dict(size=4, color='red'),
        text=names,
        name='Satellites'
    ))

    # Add mesh connections based on proximity
    for i in range(len(satellites)):
        for j in range(i + 1, len(satellites)):
            dist = np.sqrt((lats[i] - lats[j])**2 + (lons[i] - lons[j])**2)
            if dist < 15:  # Close enough for a mesh link
                fig.add_trace(go.Scattergeo(
                    lon=[lons[i], lons[j]],
                    lat=[lats[i], lats[j]],
                    mode='lines',
                    line=dict(width=1, color='blue'),
                    showlegend=False
                ))

    # Update layout
    fig.update_geos(
        showland=True,
        landcolor="lightgray",
        showocean=True,
        oceancolor="lightblue"
    )

    fig.update_layout(
        title="Real-Time Satellite Mesh Network",
        height=800,
        margin={"r": 0, "t": 40, "l": 0, "b": 0}
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
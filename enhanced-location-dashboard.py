# Import necessary libraries
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
from urllib.parse import parse_qs, unquote, quote
import plotly.graph_objects as go
from shapely import wkt
import numpy as np
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Read the data with correct encoding
try:
    df = pd.read_csv("output_location_differences.csv", encoding='cp1252')
except:
    # Fallback to UTF-8 if cp1252 fails
    df = pd.read_csv("output_location_differences.csv", encoding='utf-8')

# Ensure numeric columns are properly typed
df['area'] = pd.to_numeric(df['area'], errors='coerce')
df['shape_index'] = pd.to_numeric(df['shape_index'], errors='coerce')

# Process main table: deduplicate Category + sub
df_main = df[['category', 'sub']].drop_duplicates().reset_index(drop=True)
df_main["RowSpan"] = df_main.groupby("category")["sub"].transform("count")

# Initialize Dash app
app = Dash(__name__)
app.config.suppress_callback_exceptions = True

# Style definitions
header_style = {
    'backgroundColor': 'lightgrey',
    'fontWeight': 'bold',
    'padding': '10px',
    'textAlign': 'center',
    'border': '1px solid #ddd'
}

cell_style = {
    'border': '1px solid #ddd',
    'padding': '10px',
    'textAlign': 'center',
    'verticalAlign': 'middle'
}

link_style = {
    'textDecoration': 'none',
    'color': '#0066cc'
}

map_style = {
    'height': '500px',
    'margin': '20px',
    'border': '1px solid #ddd',
    'borderRadius': '5px'
}

# Function to convert from Web Mercator to WGS84
def mercator_to_wgs84(x, y):
    """Convert Web Mercator (EPSG:3857) coordinates to WGS84 (EPSG:4326)"""
    # Earth radius in meters
    R = 6378137
    # Convert x-coordinate
    lon = (x * 180) / (R * np.pi)
    # Convert y-coordinate
    lat_rad = np.arcsin(np.tanh(y / R))
    lat = lat_rad * 180 / np.pi
    return lon, lat

# Function to create map from multiple geometries
def create_map(filtered_df):
    """Create a map with multiple geometries in different colors"""
    fig = go.Figure()
    
    # If there's no data, return empty figure
    if filtered_df.empty:
        return fig
    
    # Generate distinct colors for each geometry
    n = len(filtered_df)
    colors = []
    for i in range(n):
        # Use HSL color to ensure distinct, evenly spaced colors
        hue = i / n * 360
        # Increased transparency by changing the alpha value from 0.6 to 0.4
        colors.append(f'rgba({int(255 * (1 + np.sin(hue * np.pi / 180)) / 2)},{int(255 * (1 + np.sin((hue + 120) * np.pi / 180)) / 2)},{int(255 * (1 + np.sin((hue + 240) * np.pi / 180)) / 2)},0.4)')
    
    # Add each geometry to the map
    all_lats = []
    all_lons = []
    
    for i, (idx, row) in enumerate(filtered_df.iterrows()):
        try:
            if pd.isna(row['geometry']) or not row['geometry']:
                continue
                
            geom = wkt.loads(row['geometry'])
            
            # Format hover text with proper handling of NaN values
            area_text = f"Area: {row['area']:.2f}" if not pd.isna(row['area']) else "Area: N/A"
            shape_index_text = f"Shape Index: {row['shape_index']:.2f}" if not pd.isna(row['shape_index']) else "Shape Index: N/A"
            # wrong_text = f"Wrong: {row['wrong']}" if not pd.isna(row['wrong']) else "Wrong: N/A"
            response_text = f"Response: {row['response']}" if not pd.isna(row['response']) else "Response: N/A"
            olc_text = f"OLC: {row['OLCs']}" if not pd.isna(row['OLCs']) else "OLC: N/A"
            
            hover_text = f"{response_text}<br>{olc_text}<br>{area_text}<br>{shape_index_text}<br>"
            
            if geom.geom_type == 'Polygon':
                # Get coordinates from polygon exterior
                coords = list(geom.exterior.coords)
                lons = []
                lats = []
                
                # Convert each coordinate from Web Mercator to WGS84
                for x, y in coords:
                    lon, lat = mercator_to_wgs84(x, y)
                    lons.append(lon)
                    lats.append(lat)
                
                all_lats.extend(lats)
                all_lons.extend(lons)
                
                # Add the polygon as a filled area
                fig.add_trace(go.Scattermapbox(
                    fill="toself",
                    lon=lons,
                    lat=lats,
                    marker={'color': 'black', 'size': 2},  # Reduced marker size
                    fillcolor=colors[i % len(colors)],
                    name=f"Row {i+1}",
                    hoverinfo="text",
                    text=hover_text
                ))
            elif geom.geom_type == 'LineString':
                # Get coordinates from line
                coords = list(geom.coords)
                lons = []
                lats = []
                
                # Convert each coordinate from Web Mercator to WGS84
                for x, y in coords:
                    lon, lat = mercator_to_wgs84(x, y)
                    lons.append(lon)
                    lats.append(lat)
                
                all_lats.extend(lats)
                all_lons.extend(lons)
                
                # Add the line
                fig.add_trace(go.Scattermapbox(
                    mode="lines",
                    lon=lons,
                    lat=lats,
                    line={'width': 3, 'color': colors[i % len(colors)].replace('0.4)', '0.8)')},  # Increased line opacity
                    name=f"Row {i+1}",
                    hoverinfo="text",
                    text=hover_text
                ))
            elif geom.geom_type == 'Point':
                # Convert point from Web Mercator to WGS84
                lon, lat = mercator_to_wgs84(geom.x, geom.y)
                
                # Add the point
                fig.add_trace(go.Scattermapbox(
                    mode="markers",
                    lon=[lon],
                    lat=[lat],
                    marker={'size': 10, 'color': colors[i % len(colors)].replace('0.4)', '0.8)')},  # Increased marker opacity
                    name=f"Row {i+1}",
                    hoverinfo="text",
                    text=hover_text
                ))
                all_lats.append(lat)
                all_lons.append(lon)
            elif geom.geom_type == 'MultiPolygon':
                # Handle MultiPolygon geometries
                for poly in geom.geoms:
                    # Get coordinates from polygon exterior
                    coords = list(poly.exterior.coords)
                    lons = []
                    lats = []
                    
                    # Convert each coordinate from Web Mercator to WGS84
                    for x, y in coords:
                        lon, lat = mercator_to_wgs84(x, y)
                        lons.append(lon)
                        lats.append(lat)
                    
                    all_lats.extend(lats)
                    all_lons.extend(lons)
                    
                    # Add each polygon as a filled area with the same color
                    fig.add_trace(go.Scattermapbox(
                        fill="toself",
                        lon=lons,
                        lat=lats,
                        marker={'color': 'black', 'size': 2},  # Reduced marker size
                        fillcolor=colors[i % len(colors)],
                        name=f"Row {i+1}",
                        hoverinfo="text",
                        text=hover_text
                    ))
        except Exception as e:
            print(f"Error processing geometry at row {i}: {e}")
    
    # Set the map center and zoom
    if all_lats and all_lons:
        center_lat = sum(all_lats) / len(all_lats)
        center_lon = sum(all_lons) / len(all_lons)
        
        # Use fixed zoom level that works well
        zoom = 15
        
        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox=dict(
                center=dict(lat=center_lat, lon=center_lon),
                zoom=zoom
            ),
            margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )
    
    return fig

# Main page layout (with search box)
main_layout = html.Div([
    html.H1("Location Differences Dashboard", style={'textAlign': 'center'}),
    html.Div([
        dcc.Input(id="search-input", type="text", placeholder="Enter Category or Sub"),
        html.Button("Search", id="search-button")
    ], style={'textAlign': 'center', 'marginBottom': '20px'}),
    html.Div(
        html.Table(
            id='main-table',
            style={'width': '100%', 'borderCollapse': 'collapse'},
            children=[
                html.Thead(
                    html.Tr([
                        html.Th("Category", style=header_style),
                        html.Th("Sub-Category", style=header_style)
                    ])
                ),
                html.Tbody(id="table-body")
            ]
        )
    )
])

# Detail page layout with custom HTML table for cell merging
def detail_layout(category, sub):
    filtered_df = df[(df["category"] == category) & (df["sub"] == sub)]
    
    # Create data for the HTML table with merged cells
    table_rows = []
    
    # Get unique sub value and count for merging
    unique_sub = sub
    sub_count = len(filtered_df)
    
    # Create table rows
    for i, (_, row) in enumerate(filtered_df.iterrows()):
        if i == 0:
            # First row includes the merged sub cell
            table_rows.append(
                html.Tr([
                    # Merged sub cell for first row
                    html.Td(
                        unique_sub,
                        rowSpan=sub_count,
                        style={
                            'border': '1px solid #ddd',
                            'padding': '10px',
                            'textAlign': 'center',
                            'verticalAlign': 'middle',
                            'backgroundColor': '#f5f5f5',
                            'fontWeight': 'bold'
                        }
                    ),
                    # Other cells for first row
                    html.Td(row['response'], style=cell_style),
                    html.Td(f"{row['area']:.2f}" if not pd.isna(row['area']) else "N/A", style=cell_style),
                    html.Td(f"{row['shape_index']:.2f}" if not pd.isna(row['shape_index']) else "N/A", style=cell_style),
                    # html.Td(row['wrong'], style=cell_style),
                    html.Td(row['OLCs'] if not pd.isna(row['OLCs']) else "N/A", style=cell_style)
                ])
            )
        else:
            # Subsequent rows only need the non-merged cells
            table_rows.append(
                html.Tr([
                    html.Td(row['response'], style=cell_style),
                    html.Td(f"{row['area']:.2f}" if not pd.isna(row['area']) else "N/A", style=cell_style),
                    html.Td(f"{row['shape_index']:.2f}" if not pd.isna(row['shape_index']) else "N/A", style=cell_style),
                    # html.Td(row['wrong'], style=cell_style),
                    html.Td(row['OLCs'] if not pd.isna(row['OLCs']) else "N/A", style=cell_style)
                ])
            )
    
    return html.Div([
        dcc.Link(
            "🔙 Back",
            href="/",
            style={
                'margin': '10px',
                'padding': '8px 16px',
                'backgroundColor': '#007bff',
                'color': 'white',
                'borderRadius': '4px',
                'textDecoration': 'none',
                'display': 'inline-block'
            }
        ),
        html.H2(f"Details for {category} - {sub}", style={'textAlign': 'center'}),
        
        # Custom HTML table with merged cells
        html.Table(
            style={'width': '100%', 'borderCollapse': 'collapse', 'marginBottom': '20px'},
            children=[
                html.Thead(
                    html.Tr([
                        html.Th("Sub", style=header_style),
                        html.Th("Response", style=header_style),
                        html.Th("Area", style=header_style),
                        html.Th("Shape Index", style=header_style),
                        # html.Th("Wrong", style=header_style),
                        html.Th("OLC", style=header_style)
                    ])
                ),
                html.Tbody(table_rows)
            ]
        ),
        
        dcc.Graph(
            id='geometry-map',
            figure=create_map(filtered_df),
            style=map_style
        )
    ])

# Callback functions
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'),
     Input('url', 'search')]
)
def display_page(pathname, search):
    if pathname == '/detail':
        params = parse_qs(search.lstrip('?'))
        category = unquote(params.get('category', [None])[0])
        sub = unquote(params.get('sub', [None])[0])
        return detail_layout(category, sub) if category and sub else main_layout
    return main_layout

@app.callback(
    Output("table-body", "children"),
    [Input('url', 'pathname'),
     Input('search-button', 'n_clicks')],
    [State('search-input', 'value')]
)
def update_table_body(pathname, n_clicks, search_term):
    # Filter data if search term is provided
    if search_term:
        filtered_df = df_main[
            (df_main["category"].str.contains(search_term, case=False)) | 
            (df_main["sub"].str.contains(search_term, case=False))
        ]
    else:
        filtered_df = df_main

    rows = []
    current_category = None

    for index, row in filtered_df.iterrows():
        category = row["category"]
        sub = row["sub"]

        if category != current_category:
            current_category = category
            rowspan = int(row["RowSpan"])
            rows.append(html.Tr([
                html.Td(
                    category,
                    rowSpan=rowspan,
                    style=cell_style
                ),
                html.Td(
                    dcc.Link(
                        sub,
                        href=f"/detail?category={quote(category)}&sub={quote(sub)}",
                        target="_blank",
                        style=link_style
                    ),
                    style=cell_style
                )
            ]))
        else:
            rows.append(html.Tr([
                html.Td(
                    dcc.Link(
                        sub,
                        href=f"/detail?category={quote(category)}&sub={quote(sub)}",
                        target="_blank",
                        style=link_style
                    ),
                    style=cell_style
                )
            ]))
    return rows

# App configuration
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
"""
Different Places for Same Idea Module
-----------------------------------
This module provides the layout and callbacks for the Different Places dashboard
"""

from dash import html, dcc, Input, Output, State, ALL, callback_context, callback
import pandas as pd
import json
import dash
from urllib.parse import parse_qs, unquote, quote
from shapely import wkt
import plotly.graph_objects as go
import plotly.express as px

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

# Load data function
def load_data():
    try:
        df = pd.read_csv('./different_place_for_sameidea2.csv')
    except:
        # If file doesn't exist, create empty dataframe with appropriate columns
        df = pd.DataFrame(columns=['Category', 'Groups', 'Summary', 'Keywords', 'OLCs', 'geometry'])
        
    # Process main table: deduplicate Category + Groups
    df_main = df[['Category', 'Groups']].drop_duplicates().reset_index(drop=True)
    df_main["RowSpan"] = df_main.groupby("Category")["Groups"].transform("count")
    
    return df, df_main

# Map generation function
def create_enhanced_map(geometry_data, selected_row_data):
    fig = go.Figure()
    colors = px.colors.qualitative.Plotly
    all_coords = []

    for idx, data in enumerate(geometry_data):
        geom_str = data['geometry']
        olc = data['olc']

        try:
            geom = wkt.loads(geom_str)
            print(f"Processing {geom.geom_type} with OLC: {olc}")  # Debug output

            if geom.geom_type in ['Polygon', 'LineString']:
                # Unified coordinate extraction
                if geom.geom_type == 'Polygon':
                    coords = list(geom.exterior.coords)
                else:  # LineString
                    coords = list(geom.coords)

                lons = [x for x, y in coords]
                lats = [y for x, y in coords]

                # Ensure coordinate validity
                if not all(-180 <= lon <= 180 for lon in lons):
                    print(f"Invalid longitude in {olc}")
                if not all(-90 <= lat <= 90 for lat in lats):
                    print(f"Invalid latitude in {olc}")

                color = colors[idx % len(colors)]

                # Create fill color (same as line but with transparency)
                if color.startswith('#'):
                    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                    fill_color = f"rgba({r}, {g}, {b}, 0.3)"
                else:
                    # Try to convert from rgb format
                    fill_color = color.replace('rgb', 'rgba').replace(')', ', 0.3)')

                # Set fill condition
                is_selected = selected_row_data and selected_row_data[0]['OLCs'] == olc
                fill = "toself" if geom.geom_type == 'Polygon' else None

                # Use lines+markers mode, but set markers to be very small
                fig.add_trace(go.Scattermapbox(
                    mode='lines+markers',  # Keep markers but make them very small
                    lon=lons,
                    lat=lats,
                    line=dict(width=3, color=color),  # Adjust line width
                    marker=dict(size=2, color=color),  # Make marker points very small
                    name=f'{olc}',
                    hoverinfo='text',
                    hovertext=f"OLC: {olc}<br>Type: {geom.geom_type}",
                    fill=fill,
                    fillcolor=fill_color
                ))

                all_coords.extend(coords)

        except Exception as e:
            print(f"Error processing geometry {idx}: {str(e)}")
            continue

    if all_coords:
        # Calculate coordinate range
        lons = [x for x, y in all_coords]
        lats = [y for x, y in all_coords]
        center_lon = sum(lons) / len(lons)
        center_lat = sum(lats) / len(lats)

        zoom = 16  # Adjust based on actual needs

        fig.update_layout(
            mapbox=dict(
                style="carto-positron",
                zoom=zoom,
                center=dict(lat=center_lat, lon=center_lon)
            ),
            legend=dict(title='Open Location Codes',
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01)
        )
    else:
        fig.add_annotation(text="No valid data", showarrow=False)

    return fig

# Main layout generator
def get_main_layout():
    return html.Div([
        html.H1("Different Places for Same Idea", style={'textAlign': 'center'}),
        html.Div(
            html.Table(
                style={'width': '100%', 'borderCollapse': 'collapse'},
                children=[
                    html.Thead(
                        html.Tr([
                            html.Th("Category", style=header_style),
                            html.Th("Groups", style=header_style)
                        ])
                    ),
                    html.Tbody(id="diff-table-body")
                ]
            )
        )
    ])

# Detail page layout
def get_detail_layout(category=None, group=None):
    # Handle case where parameters are not provided
    if not category or not group:
        return html.Div([
            html.Button(
                "🔙 Back to Dashboard",
                id="diff-back-to-main-btn",
                style={
                    'margin': '10px',
                    'padding': '8px 16px',
                    'backgroundColor': '#007bff',
                    'color': 'white',
                    'borderRadius': '4px',
                    'border': 'none',
                    'cursor': 'pointer',
                    'display': 'inline-block'
                }
            ),
            html.H3("Please select a category and group from the main page", 
                   style={'textAlign': 'center', 'marginTop': '50px', 'color': '#666'})
        ])
    
    df, _ = load_data()
    filtered_df = df[(df["Category"] == category) & (df["Groups"] == group)]
    
    if filtered_df.empty:
        return html.Div([
            html.Button(
                "🔙 Back to Dashboard",
                id="diff-back-to-main-btn",
                style={
                    'margin': '10px',
                    'padding': '8px 16px',
                    'backgroundColor': '#007bff',
                    'color': 'white',
                    'borderRadius': '4px',
                    'border': 'none',
                    'cursor': 'pointer',
                    'display': 'inline-block'
                }
            ),
            html.H3(f"No data found for {category} - {group}", 
                   style={'textAlign': 'center', 'marginTop': '50px', 'color': '#666'})
        ])

    # Extract unique values
    group_value = filtered_df['Groups'].iloc[0]
    summary_value = filtered_df['Summary'].iloc[0]
    keywords_value = filtered_df['Keywords'].iloc[0]

    # Row count
    num_rows = len(filtered_df)

    # Prepare map data
    geometry_data = filtered_df[['geometry', 'OLCs']] \
        .rename(columns={'OLCs': 'olc'}).to_dict('records')

    # Create OLC cells, each with a click event
    olc_cells = []
    for i in range(num_rows):
        olc_value = filtered_df['OLCs'].iloc[i] if i < len(filtered_df) else ""
        # Create a clickable div for each OLC cell
        olc_cell = html.Td(
            html.Button(
                olc_value,
                id={'type': 'olc-button', 'index': i},
                style={
                    'width': '100%',
                    'textAlign': 'center',
                    'backgroundColor': 'transparent',
                    'border': 'none',
                    'cursor': 'pointer',
                    'fontFamily': 'inherit',
                    'fontSize': 'inherit',
                    'padding': '0',
                    'color': 'inherit'
                }
            ),
            style=cell_style
        )
        olc_cells.append(olc_cell)

    # Create geometry cells
    geometry_cells = []
    for i in range(num_rows):
        geom_value = filtered_df['geometry'].iloc[i] if i < len(filtered_df) else ""
        geom_cell = html.Td(geom_value, style=cell_style)
        geometry_cells.append(geom_cell)

    # Create table rows
    table_rows = []

    # First row includes merged cells
    first_row = html.Tr([
        # Merged cell - Groups
        html.Td(
            group_value,
            rowSpan=num_rows,
            style={
                'border': '1px solid #ddd',
                'padding': '10px',
                'textAlign': 'center',
                'verticalAlign': 'middle',
                'backgroundColor': '#f8f9fa',
                'fontWeight': 'bold'
            }
        ),
        # Merged cell - Summary
        html.Td(
            summary_value,
            rowSpan=num_rows,
            style={
                'border': '1px solid #ddd',
                'padding': '10px',
                'textAlign': 'center',
                'verticalAlign': 'middle',
                'backgroundColor': '#f8f9fa',
                'fontWeight': 'bold'
            }
        ),
        # Merged cell - Keywords
        html.Td(
            keywords_value,
            rowSpan=num_rows,
            style={
                'border': '1px solid #ddd',
                'padding': '10px',
                'textAlign': 'center',
                'verticalAlign': 'middle',
                'backgroundColor': '#f8f9fa',
                'fontWeight': 'bold'
            }
        ),
        # First row's OLCs and Geometry
        olc_cells[0] if olc_cells else html.Td("", style=cell_style),
        geometry_cells[0] if geometry_cells else html.Td("", style=cell_style)
    ])
    table_rows.append(first_row)

    # Add remaining rows
    for i in range(1, num_rows):
        row = html.Tr([
            olc_cells[i] if i < len(olc_cells) else html.Td("", style=cell_style),
            geometry_cells[i] if i < len(geometry_cells) else html.Td("", style=cell_style)
        ])
        table_rows.append(row)

    return html.Div([
        html.Div(
            html.Button(
                "🔙 Back to Main",
                id="diff-back-to-main-btn",
                style={
                    'margin': '10px',
                    'padding': '8px 16px',
                    'backgroundColor': '#007bff',
                    'color': 'white',
                    'borderRadius': '4px',
                    'border': 'none',
                    'cursor': 'pointer',
                    'display': 'inline-block'
                }
            )
        ),
        html.H2(f"Details for {category} - {group}", style={'textAlign': 'center'}),
        # Use HTML table to implement real cell merging
        html.Div(
            html.Table(
                style={'width': '100%', 'borderCollapse': 'collapse', 'margin': '20px'},
                children=[
                    # Table header
                    html.Thead(
                        html.Tr([
                            html.Th("Groups", style=header_style),
                            html.Th("Summary", style=header_style),
                            html.Th("Keywords", style=header_style),
                            html.Th("OLCs", style=header_style),
                            html.Th("Geometry", style=header_style),
                        ])
                    ),
                    # Table body
                    html.Tbody(table_rows)
                ]
            )
        ),

        # Store selected OLC
        dcc.Store(id='diff-selected-row-data', data=[]),

        # Map display
        dcc.Graph(
            id='diff-geometry-map',
            figure=create_enhanced_map(geometry_data, []),
            style=map_style
        )
    ])

# Register all callbacks for this module
def register_callbacks(app):
    @app.callback(
        Output("diff-table-body", "children"),
        [Input("diff-url", "pathname")]
    )
    def update_table_body(_):
        _, df_main = load_data()
        rows = []
        current_category = None

        for i, row in df_main.iterrows():
            category = row["Category"]
            group = row["Groups"]

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
                        html.Button(
                            group,
                            id={"type": "diff-group-button", "index": i, "category": category, "group": group},
                            style={
                                'width': '100%',
                                'textAlign': 'left',
                                'backgroundColor': 'transparent',
                                'border': 'none',
                                'cursor': 'pointer',
                                'fontFamily': 'inherit',
                                'fontSize': 'inherit',
                                'padding': '10px',
                                'color': '#0066cc',
                                'textDecoration': 'underline'
                            }
                        ),
                        style=cell_style
                    )
                ]))
            else:
                rows.append(html.Tr([
                    html.Td(
                        html.Button(
                            group,
                            id={"type": "diff-group-button", "index": i, "category": category, "group": group},
                            style={
                                'width': '100%',
                                'textAlign': 'left',
                                'backgroundColor': 'transparent',
                                'border': 'none',
                                'cursor': 'pointer',
                                'fontFamily': 'inherit',
                                'fontSize': 'inherit',
                                'padding': '10px',
                                'color': '#0066cc',
                                'textDecoration': 'underline'
                            }
                        ),
                        style=cell_style
                    )
                ]))
        
        if not rows:
            rows = [html.Tr(html.Td("No data available", colSpan=2, style={'textAlign': 'center', 'padding': '20px'}))]
            
        return rows
    
    @app.callback(
        Output("diff-selected-row-data", "data"),
        [Input({"type": "olc-button", "index": ALL}, "n_clicks")],
        [State("diff-state", "data")]
    )
    def handle_olc_button_click(n_clicks, state):
        ctx = callback_context
        if not ctx.triggered or not any(n_clicks):
            return []

        # Get the clicked button ID
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if not button_id:
            return []

        try:
            # Parse button index
            button_id_dict = json.loads(button_id)
            button_index = button_id_dict.get('index', 0)

            # Get current category and group
            category = state.get('category')
            group = state.get('group')

            if category and group:
                df, _ = load_data()
                filtered_df = df[(df["Category"] == category) & (df["Groups"] == group)]
                if button_index < len(filtered_df):
                    selected_row = filtered_df.iloc[button_index]
                    return [{'OLCs': selected_row['OLCs']}]
        except Exception as e:
            print(f"Error handling button click: {str(e)}")

        return []
    
    @app.callback(
        Output("diff-geometry-map", "figure"),
        [Input("diff-selected-row-data", "data"),
         Input("diff-state", "data")]
    )
    def update_map(selected_row_data, state):
        category = state.get('category')
        group = state.get('group')

        if category and group:
            df, _ = load_data()
            filtered_df = df[(df["Category"] == category) & (df["Groups"] == group)]
            geometry_data = filtered_df[['geometry', 'OLCs']] \
                .rename(columns={'OLCs': 'olc'}).to_dict('records')
            return create_enhanced_map(geometry_data, selected_row_data)
        return go.Figure()  # Return empty figure
    
    @app.callback(
        Output("diff-state", "data"),
        [Input({"type": "diff-group-button", "index": dash.ALL, "category": dash.ALL, "group": dash.ALL}, "n_clicks"),
         Input("diff-back-to-main-btn", "n_clicks")],
        [State("diff-state", "data")]
    )
    def update_page_state(group_clicks, back_clicks, current_state):
        ctx = dash.callback_context
        
        if not ctx.triggered:
            return current_state
            
        # Get the ID of the component that triggered the callback
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Handle back button
        if trigger_id == "diff-back-to-main-btn":
            return {'view': 'main', 'category': None, 'group': None}
            
        # Handle group selection
        try:
            trigger = json.loads(trigger_id)
            if trigger.get('type') == 'diff-group-button':
                return {
                    'view': 'detail',
                    'category': trigger.get('category'),
                    'group': trigger.get('group')
                }
        except:
            pass
            
        return current_state

# Combined layout for this module with state management
def get_layout(app):
    """Initialize the dashboard layout and register callbacks"""
    
    # Register callbacks for this module
    register_callbacks(app)
    
    # Create main layout with state management
    return html.Div([
        dcc.Location(id="diff-url", refresh=False),
        dcc.Store(id="diff-state", data={'view': 'main', 'category': None, 'group': None}),
        html.Div(id='diff-page-content')
    ])

# Handle page content based on state
@callback(
    Output('diff-page-content', 'children'),
    [Input('diff-state', 'data')])
def render_page_content(state):
    view = state.get('view', 'main')
    
    if view == 'main':
        return get_main_layout()
    elif view == 'detail':
        return get_detail_layout(state.get('category'), state.get('group'))
    else:
        return get_main_layout()

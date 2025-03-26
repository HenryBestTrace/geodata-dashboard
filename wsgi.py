from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from shapely import wkt
import numpy as np

# 导入主应用布局相关组件
from main_app_test import create_header, create_dashboard_cards, dashboard_items

# 创建新的Dash应用实例，并确保它使用与原应用相同的样式
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True
)

# 设置server变量，这是gunicorn需要的
server = app.server

# 从主应用导入首页布局
home_layout = html.Div(
    [
        # 现代设计的头部
        create_header(),
        
        # 主要内容容器
        dbc.Container(
            [
                # 标题部分
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span("Choose a ", style={"color": "#666"}),
                                html.Span("Dashboard", style={"color": "#4361ee"})
                            ],
                            className="h2 mb-4 d-flex justify-content-center gap-2"
                        ),
                        html.P(
                            "Select one of the dashboards below to begin your exploration",
                            className="text-muted text-center mb-5",
                            style={"fontSize": "18px"}
                        )
                    ],
                    className="mb-4 text-center"
                ),
                
                # 仪表板卡片
                create_dashboard_cards(),
                
                # 底部部分
                html.Div(
                    [
                        html.Div(className="separator my-5"),
                        # 底部内容从main_app_test.py复制
                        # ...省略以保持简洁...
                    ],
                    className="row mt-5 pt-3 feature-section"
                ),
                
                # 页脚
                html.Footer(
                    dbc.Container(
                        [
                            html.Hr(className="my-5"),
                            html.Div(
                                [
                                    html.P(
                                        "Geodata Visualization Dashboard (Team 10)© 2025",
                                        className="mb-0 text-center text-muted"
                                    ),
                                    html.P(
                                        "Created for advanced data analysis",
                                        className="mb-0 text-center text-muted small"
                                    )
                                ]
                            )
                        ]
                    ),
                    className="mt-5 pb-4"
                )
            ],
            className="py-4"
        )
    ],
    style={"backgroundColor": "#fbfbfd"}
)

# Location Differences Dashboard 功能代码
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
            wrong_text = f"Wrong: {row['wrong']}" if not pd.isna(row['wrong']) else "Wrong: N/A"
            response_text = f"Response: {row['response']}" if not pd.isna(row['response']) else "Response: N/A"
            olc_text = f"OLC: {row['OLCs']}" if 'OLCs' in row and not pd.isna(row['OLCs']) else "OLC: N/A"
            
            hover_text = f"{response_text}<br>{olc_text}<br>{area_text}<br>{shape_index_text}<br>{wrong_text}"
            
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
                # 线条处理代码
                pass
            elif geom.geom_type == 'Point':
                # 点处理代码
                pass
            elif geom.geom_type == 'MultiPolygon':
                # 多边形处理代码
                pass
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

# Location Differences Dashboard布局
def location_differences_layout():
    try:
        df = pd.read_csv("output_location_differences.csv")
        df['area'] = pd.to_numeric(df['area'], errors='coerce')
        df['shape_index'] = pd.to_numeric(df['shape_index'], errors='coerce')
        df_main = df[['category', 'sub']].drop_duplicates().reset_index(drop=True)
        
        return html.Div([
            html.H1("Location Differences Dashboard", style={'textAlign': 'center'}),
            html.Div([
                dcc.Input(id="location-search-input", type="text", placeholder="Enter Category or Sub"),
                html.Button("Search", id="location-search-button")
            ], style={'textAlign': 'center', 'marginBottom': '20px'}),
            html.Div(id="location-table-container")
        ])
    except Exception as e:
        return html.Div([
            html.H3("Error loading Location Differences Dashboard"),
            html.P(f"Error: {str(e)}"),
            html.P("Please check that the data file 'output_location_differences.csv' exists.")
        ])

# 其他子仪表板的布局函数
def response_summaries_layout():
    return html.Div([
        html.H1("Response Summaries Dashboard", style={'textAlign': 'center'}),
        html.P("This dashboard is currently under integration.")
    ])

def conceptual_responses_layout():
    return html.Div([
        html.H1("Conceptual Responses Dashboard", style={'textAlign': 'center'}),
        html.P("This dashboard is currently under integration.")
    ])

def different_places_layout():
    return html.Div([
        html.H1("Different Places Dashboard", style={'textAlign': 'center'}),
        html.P("This dashboard is currently under integration.")
    ])

# 应用布局和回调
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content"),
    html.Div(
        dbc.Button(
            [
                html.I(className="fas fa-home me-2"),
                "Back to Home"
            ],
            id="home-button",
            href="/",
            color="primary",
            className="mt-3 px-4 py-2",
            style={"display": "none", "borderRadius": "30px", "boxShadow": "0 4px 10px rgba(0,0,0,0.1)"}
        ),
        id="home-button-container",
        className="text-center mb-3"
    )
])

@app.callback(
    [Output("page-content", "children"),
     Output("home-button", "style")],
    [Input("url", "pathname")]
)
def display_page(pathname):
    # 显示返回按钮的样式
    button_style = {"display": "block", "borderRadius": "30px", "boxShadow": "0 4px 10px rgba(0,0,0,0.1)"}
    hide_button = {"display": "none"}
    
    # 主页
    if pathname == "/" or not pathname:
        return home_layout, hide_button
    
    # 子仪表板页面
    elif pathname == "/geometry":
        return location_differences_layout(), button_style
    elif pathname == "/response":
        return response_summaries_layout(), button_style
    elif pathname == "/conceptual":
        return conceptual_responses_layout(), button_style
    elif pathname == "/different":
        return different_places_layout(), button_style
    else:
        return html.Div([
            html.H3("404 - Page not found"),
            html.P(f"The path {pathname} does not exist in this application."),
            dcc.Link("Return to home page", href="/")
        ]), button_style

# 如果需要，可以添加更多回调函数来处理子仪表板的交互

if __name__ == "__main__":
    app.run_server(debug=False)

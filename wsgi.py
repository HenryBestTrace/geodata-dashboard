import os
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
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.I(
                                            className="fas fa-chart-line me-3",
                                            style={"fontSize": "32px", "color": "#4361ee"}
                                        ),
                                        html.Div(
                                            [
                                                html.H5("Advanced Analytics", className="mb-2"),
                                                html.P(
                                                    "Gain deeper insights with our comprehensive visualization tools",
                                                    className="text-muted mb-0"
                                                )
                                            ]
                                        )
                                    ],
                                    className="d-flex align-items-center mb-4"
                                ),
                                html.Div(
                                    [
                                        html.I(
                                            className="fas fa-map-marked-alt me-3",
                                            style={"fontSize": "32px", "color": "#38b000"}
                                        ),
                                        html.Div(
                                            [
                                                html.H5("Geospatial Mapping", className="mb-2"),
                                                html.P(
                                                    "Explore geographical patterns and spatial relationships in your data",
                                                    className="text-muted mb-0"
                                                )
                                            ]
                                        )
                                    ],
                                    className="d-flex align-items-center"
                                )
                            ],
                            className="col-md-6"
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.I(
                                            className="fas fa-comments me-3",
                                            style={"fontSize": "32px", "color": "#8338ec"}
                                        ),
                                        html.Div(
                                            [
                                                html.H5("Response Analysis", className="mb-2"),
                                                html.P(
                                                    "Analyze and categorize responses for better decision making",
                                                    className="text-muted mb-0"
                                                )
                                            ]
                                        )
                                    ],
                                    className="d-flex align-items-center mb-4"
                                ),
                                html.Div(
                                    [
                                        html.I(
                                            className="fas fa-project-diagram me-3",
                                            style={"fontSize": "32px", "color": "#ff5400"}
                                        ),
                                        html.Div(
                                            [
                                                html.H5("Comparative Insights", className="mb-2"),
                                                html.P(
                                                    "Compare ideas across different locations and contexts",
                                                    className="text-muted mb-0"
                                                )
                                            ]
                                        )
                                    ],
                                    className="d-flex align-items-center"
                                )
                            ],
                            className="col-md-6"
                        )
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

# Location Differences Dashboard布局
def location_differences_layout():
    try:
        # 列出当前目录的文件，用于调试
        current_files = os.listdir('.')
        print(f"Current directory files: {current_files}")
        
        # 尝试使用不同的编码读取文件
        file_path = "output_location_differences.csv"
        if file_path not in current_files:
            return html.Div([
                html.H3("Error loading Location Differences Dashboard"),
                html.P(f"Error: File '{file_path}' not found in current directory."),
                html.P("Available files:"),
                html.Ul([html.Li(file) for file in current_files])
            ])
            
        try:
            # 首先尝试使用cp1252编码
            df = pd.read_csv(file_path, encoding='cp1252')
        except UnicodeDecodeError:
            try:
                # 然后尝试使用utf-8编码
                df = pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    # 最后尝试使用latin1编码(几乎可以读取任何文件，但可能有字符替换)
                    df = pd.read_csv(file_path, encoding='latin1')
                except Exception as e:
                    return html.Div([
                        html.H3("Error loading Location Differences Dashboard"),
                        html.P(f"Error reading CSV with multiple encodings: {str(e)}"),
                        html.P("Please check that the data file is properly encoded.")
                    ])
            
        # 确保数值列正确类型化
        df['area'] = pd.to_numeric(df['area'], errors='coerce')
        df['shape_index'] = pd.to_numeric(df['shape_index'], errors='coerce')
        
        # 这里展示一个简单的数据表而不是复杂的交互式仪表板，作为示例
        return html.Div([
            html.H1("Location Differences Dashboard", style={'textAlign': 'center', 'marginBottom': '20px'}),
            # html.H1("Location Differences Dashboard", style={'textAlign': 'center', 'marginBottom': '20px'}),
            html.Div([
                html.P("Data file loaded successfully!", className="text-success"),
                html.P(f"Found {len(df)} records in dataset.")
            ], style={'textAlign': 'center', 'marginBottom': '20px'}),
            
            # 简单的数据表显示
            html.Div([
                html.H3("Sample Data", style={'textAlign': 'center'}),
                dbc.Table.from_dataframe(
                    df.head(10),
                    striped=True,
                    bordered=True,
                    hover=True,
                    responsive=True
                )
            ]),
            
            # 这里可以添加更多交互组件，如筛选器、图表等
            html.Div([
                html.H3("Map Visualization", style={'textAlign': 'center', 'marginTop': '30px'}),
                html.P("Select a category and sub to view on map:"),
                dcc.Dropdown(
                    id='category-dropdown',
                    options=[{'label': cat, 'value': cat} for cat in df['category'].unique()],
                    value=df['category'].iloc[0] if not df.empty else None,
                    style={'marginBottom': '10px'}
                ),
                dcc.Dropdown(
                    id='sub-dropdown',
                    placeholder="Select a sub-category",
                ),
                dcc.Graph(
                    id='location-map',
                    style={'height': '600px', 'marginTop': '20px'}
                )
            ])
        ])
    except Exception as e:
        # 捕获所有异常，显示详细错误信息
        import traceback
        error_details = traceback.format_exc()
        
        return html.Div([
            html.H3("Error loading Location Differences Dashboard", style={'color': 'red'}),
            html.P(f"Error: {str(e)}"),
            html.Details([
                html.Summary("Error Details (click to expand)"),
                html.Pre(error_details, style={'whiteSpace': 'pre-wrap', 'overflowX': 'auto', 'backgroundColor': '#f8f9fa', 'padding': '15px'})
            ]),
            html.P("Please check that the data file 'output_location_differences.csv' exists and is properly encoded."),
            html.Div([
                html.H4("Available Files:"),
                html.Ul([html.Li(file) for file in os.listdir('.')])
            ])
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

# 为Location Differences仪表板添加回调函数
@app.callback(
    Output('sub-dropdown', 'options'),
    Input('category-dropdown', 'value')
)
def update_sub_dropdown(selected_category):
    if not selected_category:
        return []
    
    try:
        # 读取数据，与前面相同的编码处理
        try:
            df = pd.read_csv("output_location_differences.csv", encoding='cp1252')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv("output_location_differences.csv", encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv("output_location_differences.csv", encoding='latin1')
        
        # 筛选选定类别的子类别
        filtered_df = df[df['category'] == selected_category]
        subs = filtered_df['sub'].unique()
        
        return [{'label': sub, 'value': sub} for sub in subs]
    except Exception as e:
        print(f"Error updating sub dropdown: {str(e)}")
        return []

@app.callback(
    Output('location-map', 'figure'),
    [Input('category-dropdown', 'value'),
     Input('sub-dropdown', 'value')]
)
def update_map(selected_category, selected_sub):
    if not selected_category or not selected_sub:
        return go.Figure()
    
    try:
        # 读取数据，与前面相同的编码处理
        try:
            df = pd.read_csv("output_location_differences.csv", encoding='cp1252')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv("output_location_differences.csv", encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv("output_location_differences.csv", encoding='latin1')
        
        # 确保数值列正确类型化
        df['area'] = pd.to_numeric(df['area'], errors='coerce')
        df['shape_index'] = pd.to_numeric(df['shape_index'], errors='coerce')
        
        # 筛选数据
        filtered_df = df[(df['category'] == selected_category) & (df['sub'] == selected_sub)]
        
        # 创建地图
        return create_map(filtered_df)
    except Exception as e:
        print(f"Error updating map: {str(e)}")
        return go.Figure()

if __name__ == "__main__":
    app.run_server(debug=False)

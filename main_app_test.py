import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import os
import sys
import importlib.util
import traceback
from PIL import Image, ImageDraw
import webbrowser
import pandas as pd
from urllib.parse import parse_qs, unquote, quote
import plotly.graph_objects as go
from shapely import wkt
import numpy as np
import warnings

# Initialize the main Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)
server = app.server  # Needed for Render deployment

# Define dashboard items with icons
dashboard_items = [
    {
        "id": "geometry-card",
        "title": "Location Differences",
        "description": "Analyze geographic location differences with map visualization",
        "icon": "fa-solid fa-map-location-dot",
        "image": "./assets/1.png",
        "path": "/geometry",
        "module_path": "enhanced_location_dashboard_module.py",
        "module_name": "location_differences",
        "color": "#4361ee"  # Custom blue color
    },
    {
        "id": "response-card",
        "title": "Response Summaries",
        "description": "Response data analysis and summaries",
        "icon": "fa-solid fa-chart-column",
        "image": "./assets/2.png",
        "path": "/response",
        "module_path": "classified_response_summary_module.py",
        "module_name": "classified_response",
        "color": "#38b000"  # Custom green color
    },
    {
        "id": "conceptual-card",
        "title": "Conceptual Responses",
        "description": "Conceptual classified response exploration",
        "icon": "fa-solid fa-brain",
        "image": "./assets/3.png",
        "path": "/conceptual",
        "module_path": "conceptual_classified_responses_module.py",
        "module_name": "conceptual_responses",
        "color": "#8338ec"  # Custom purple color
    },
    {
        "id": "different-card",
        "title": "Different Places",
        "description": "Comparison of same ideas across different locations",
        "icon": "fa-solid fa-location-crosshairs",
        "image": "./assets/4.png",
        "path": "/different",
        "module_path": "different_place_for_sameidea_module.py",
        "module_name": "different_place",
        "color": "#ff5400"  # Custom orange color
    }
]

# Create enhanced dashboard cards with modern design
def create_dashboard_cards():
    cards = []
    
    for item in dashboard_items:
        # Create a modern card design with subtle effects
        card = dbc.Col(
            html.Div(
                [
                    # Card with image, icon, title and content
                    html.Div(
                        [
                            # Top image with overlay effect
                            html.Div(
                                [
                                    # Background image
                                    html.Div(
                                        style={
                                            "backgroundImage": f"url({item['image']})",
                                            "backgroundSize": "cover",
                                            "backgroundPosition": "center",
                                            "height": "200px",
                                            "borderRadius": "12px 12px 0 0",
                                            "position": "relative"
                                        }
                                    ),
                                    # Icon in circle overlay
                                    html.Div(
                                        html.I(className=item["icon"]),
                                        style={
                                            "position": "absolute",
                                            "bottom": "-25px",
                                            "right": "20px",
                                            "backgroundColor": item["color"],
                                            "color": "white",
                                            "width": "50px",
                                            "height": "50px",
                                            "borderRadius": "50%",
                                            "display": "flex",
                                            "alignItems": "center",
                                            "justifyContent": "center",
                                            "fontSize": "22px",
                                            "boxShadow": "0 4px 8px rgba(0,0,0,0.1)"
                                        }
                                    )
                                ],
                                style={"position": "relative"}
                            ),
                            
                            # Card content
                            html.Div(
                                [
                                    # Title
                                    html.H4(
                                        item["title"], 
                                        style={
                                            "color": "#333", 
                                            "fontWeight": "600",
                                            "marginBottom": "12px",
                                            "borderBottom": f"3px solid {item['color']}",
                                            "paddingBottom": "8px",
                                            "display": "inline-block"
                                        }
                                    ),
                                    
                                    # Description
                                    html.P(
                                        item["description"],
                                        style={
                                            "color": "#666",
                                            "fontSize": "16px",
                                            "marginBottom": "25px"
                                        }
                                    ),
                                    
                                    # Button
                                    html.A(
                                        [
                                            "Explore ",
                                            html.I(className="fas fa-arrow-right ms-1")
                                        ],
                                        href=item["path"],
                                        className="dashboard-button",
                                        id=f"btn-{item['id']}",
                                        style={
                                            "backgroundColor": "white",
                                            "color": item["color"],
                                            "border": f"2px solid {item['color']}",
                                            "padding": "8px 20px",
                                            "borderRadius": "30px",
                                            "textDecoration": "none",
                                            "fontWeight": "500",
                                            "display": "inline-block",
                                            "transition": "all 0.3s ease"
                                        }
                                    )
                                ],
                                style={
                                    "padding": "30px 25px 25px",
                                    "backgroundColor": "white"
                                }
                            )
                        ],
                        className="dashboard-card",
                        style={
                            "borderRadius": "12px",
                            "overflow": "hidden",
                            "boxShadow": "0 10px 30px rgba(0,0,0,0.05)",
                            "transition": "all 0.3s ease",
                            "height": "100%"
                        }
                    )
                ],
                style={"padding": "15px"}
            ),
            md=6,
            lg=3,
            className="mb-4"
        )
        cards.append(card)
    
    return dbc.Row(cards)

# Create modern header for homepage
def create_header():
    return html.Div(
        [
            dbc.Container(
                [
                    html.Div(
                        [
                            html.H1(
                                "Geodata Visualization Dashboard", 
                                className="display-4 fw-bold mb-4",
                                style={
                                    "color": "#1e1e1e",
                                    "letterSpacing": "-0.5px",
                                }
                            ),
                            html.P(
                                "Explore interactive visualizations and gain valuable insights from your data",
                                className="lead fs-4 mb-5",
                                style={"color": "#555", "maxWidth": "800px", "margin": "0 auto"}
                            ),
                            html.Div(
                                html.Div(className="header-line"),
                                style={"width": "100px", "margin": "0 auto 40px"}
                            )
                        ],
                        className="text-center py-5"
                    )
                ],
                fluid=True,
                className="py-4"
            )
        ],
        style={
            "backgroundImage": "linear-gradient(180deg, #f8f9fa, #ffffff)",
            "borderBottom": "1px solid #eaeaea",
            "marginBottom": "30px"
        }
    )

# Homepage layout with clean, modern design
home_layout = html.Div(
    [
        # Modern header
        create_header(),
        
        # Main content container
        dbc.Container(
            [
                # Section title
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
                
                # Dashboard cards
                create_dashboard_cards(),
                
                # Bottom section with more information
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
                
                # Footer section
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

# Dashboard module loader function
def load_module(module_path, module_name):
    """Safely load a module and return detailed error information if needed"""
    try:
        # Ensure we use absolute paths
        abs_module_path = os.path.abspath(module_path)
        
        # Temporarily add module directory to sys.path
        module_dir = os.path.dirname(abs_module_path)
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
            
        # Import the module
        if os.path.exists(abs_module_path):
            spec = importlib.util.spec_from_file_location(module_name, abs_module_path)
            if spec is None:
                print(f"Module not found: {abs_module_path}")
                return None, f"Module not found: {abs_module_path}"
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            
            try:
                spec.loader.exec_module(module)
                print(f"Successfully loaded module: {module_name}")
                return module, None
            except Exception as e:
                error_msg = f"Error loading module: {str(e)}\n{traceback.format_exc()}"
                print(error_msg)
                return None, error_msg
        else:
            return None, f"File not found: {abs_module_path}"
    except Exception as e:
        error_msg = f"Error importing module: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return None, error_msg

# Main application layout
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div(id="loading-container"),
        html.Div(id="debug-info", style={"padding": "10px", "background": "#f8d7da", "display": "none"}),
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
        ),
        dbc.Toast(
            id="status-toast",
            header="Status",
            is_open=False,
            dismissable=True,
            duration=5000,
            style={"position": "fixed", "top": 10, "right": 10, "zIndex": 1000}
        ),
    ]
)

# Page routing callback
@app.callback(
    [Output("page-content", "children"),
     Output("home-button", "style"),
     Output("debug-info", "children"),
     Output("debug-info", "style")],
    [Input("url", "pathname")],
)
def display_page(pathname):
    """Handle page routing for all dashboards"""
    print(f"URL path changed to: {pathname}")
    
    # Show home button style
    button_style = {"display": "block", "borderRadius": "30px", "boxShadow": "0 4px 10px rgba(0,0,0,0.1)"}
    hide_button_style = {"display": "none"}
    
    # HomePage
    if pathname == "/" or not pathname:
        return home_layout, hide_button_style, "", {"display": "none"}
    
    # Find matching dashboard
    selected_dashboard = None
    for item in dashboard_items:
        if item["path"] == pathname:
            selected_dashboard = item
            break
            
    if not selected_dashboard:
        return home_layout, hide_button_style, "Unknown path", {"display": "block", "padding": "10px", "background": "#f8d7da"}
    
    # Try to load module
    module, error = load_module(selected_dashboard["module_path"], selected_dashboard["module_name"])
    
    if error:
        debug_msg = f"Error loading {selected_dashboard['title']}: {error}"
        print(debug_msg)
        return html.Div([
            html.H4(f"Error loading {selected_dashboard['title']}"),
            html.Pre(error, style={"whiteSpace": "pre-wrap", "overflow": "auto", "maxHeight": "300px"}),
            html.Div([
                dbc.Button("Try Again", id="retry-button", color="primary", className="me-2", 
                          href=selected_dashboard["path"]),
                dbc.Button("Return Home", href="/", color="secondary")
            ], className="mt-4 d-flex justify-content-center gap-2")
        ]), button_style, debug_msg, {"display": "block", "padding": "10px", "background": "#f8d7da"}
    
    # Get the dashboard layout from the module
    try:
        dashboard_layout = html.Div([
            html.Div([
                html.I(
                    className=selected_dashboard["icon"], 
                    style={
                        "marginRight": "10px", 
                        "fontSize": "24px",
                        "color": selected_dashboard["color"]
                    }
                ),
                html.H3(
                    selected_dashboard["title"], 
                    className="mb-3",
                    style={"color": "#333"}
                ),
            ], className="d-flex align-items-center justify-content-center my-3"),
            
            # Get the layout from the module
            module.get_layout(app)
        ])
        
        return dashboard_layout, button_style, "", {"display": "none"}
    except Exception as e:
        error_msg = f"Error rendering dashboard: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return html.Div([
            html.H4(f"Error rendering {selected_dashboard['title']}"),
            html.Pre(error_msg, style={"whiteSpace": "pre-wrap", "overflow": "auto", "maxHeight": "300px"}),
            html.Div([
                dbc.Button("Try Again", id="retry-button", color="primary", className="me-2", 
                          href=selected_dashboard["path"]),
                dbc.Button("Return Home", href="/", color="secondary")
            ], className="mt-4 d-flex justify-content-center gap-2")
        ]), button_style, error_msg, {"display": "block", "padding": "10px", "background": "#f8d7da"}

# Make sure to register all callbacks from sub-modules
# This will be done dynamically when modules are loaded

# Create assets directory if needed 
if not os.path.exists("assets"):
    os.makedirs("assets")

# Create sample images if they don't exist
def create_sample_images():
    """Create sample images for dashboard cards"""
    from PIL import Image, ImageDraw
    
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    # Create four colored sample images
    colors = [
        (67, 97, 238),  # Blue
        (56, 176, 0),   # Green
        (131, 56, 236), # Purple
        (255, 84, 0)    # Orange
    ]
    
    for i, color in enumerate(colors, 1):
        img = Image.new('RGB', (400, 200), color=color)
        draw = ImageDraw.Draw(img)
        
        # Add patterns to make images more interesting
        for j in range(0, 400, 20):
            draw.line([(j, 0), (j, 200)], fill=(255, 255, 255, 50), width=1)
        for j in range(0, 200, 20):
            draw.line([(0, j), (400, j)], fill=(255, 255, 255, 50), width=1)
            
        # Draw center pattern
        draw.ellipse((150, 50, 250, 150), fill=(255, 255, 255, 100))
        
        img.save(f'assets/{i}.png')
    
    print("Created sample images in assets directory.")

# Create custom CSS file
def create_custom_css():
    """Create custom CSS for the dashboard"""
    css_file = os.path.join("assets", "custom.css")
    with open(css_file, "w") as f:
        f.write("""
        /* Enhanced Light Theme Dashboard Styles */
        
        body { 
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif; 
            background-color: #fbfbfd;
            color: #333;
        }
        
        /* Card hover effects */
        .dashboard-card {
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            background-color: white;
            border: none;
        }
        
        .dashboard-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1) !important;
        }
        
        /* Button hover effect */
        .dashboard-button:hover {
            color: white !important;
            background-color: var(--hover-color) !important;
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        /* Button color variations */
        .dashboard-card:nth-child(1) .dashboard-button { --hover-color: #4361ee; }
        .dashboard-card:nth-child(2) .dashboard-button { --hover-color: #38b000; }
        .dashboard-card:nth-child(3) .dashboard-button { --hover-color: #8338ec; }
        .dashboard-card:nth-child(4) .dashboard-button { --hover-color: #ff5400; }
        
        /* Header line */
        .header-line {
            height: 4px;
            background: linear-gradient(90deg, #4361ee, #38b000, #8338ec, #ff5400);
            border-radius: 2px;
        }
        
        /* Section separator */
        .separator {
            height: 1px;
            background: linear-gradient(90deg, transparent, #e0e0e0, transparent);
            position: relative;
        }
        
        .separator::before {
            content: '';
            position: absolute;
            width: 100px;
            height: 3px;
            background: linear-gradient(90deg, #4361ee, #38b000);
            top: -1px;
            left: 50%;
            transform: translateX(-50%);
            border-radius: 3px;
        }
        
        /* Feature section styling */
        .feature-section {
            background-color: #f8faff;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 3px 15px rgba(0, 0, 0, 0.03);
        }
        
        /* Animation for page transitions */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        #page-content {
            animation: fadeIn 0.5s ease-out;
        }
        
        /* Modern scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #c0c0c0;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #a0a0a0;
        }
        
        /* Home button styling */
        #home-button {
            transition: all 0.3s ease;
        }
        
        #home-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15) !important;
        }
        
        /* Table styling */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: center;
        }
        
        th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        
        /* Link styling */
        a {
            color: #0066cc;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        """)
    print("Created custom CSS file.")

# Initialize assets before starting the app
if __name__ == "__main__":
    # Create assets and resources
    if not os.path.exists("assets") or not all(os.path.exists(f'assets/{i}.png') for i in range(1, 5)):
        create_sample_images()
    
    # Create CSS
    create_custom_css()
    
    # Run the app
    app.run_server(debug=True)
else:
    # When deployed to Render, make sure assets are created
    if not os.path.exists("assets") or not all(os.path.exists(f'assets/{i}.png') for i in range(1, 5)):
        create_sample_images()
    
    # Create CSS
    if not os.path.exists(os.path.join("assets", "custom.css")):
        create_custom_css()

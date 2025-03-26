from dash import Dash, dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import os
import sys
import threading
import importlib.util
import traceback
from PIL import Image, ImageDraw
import random
import time
import webbrowser

# 全局变量控制浏览器是否已被打开
browser_opened = False

# Use a light modern theme with BOOTSTRAP + Font Awesome for icons
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True
)
server = app.server
# Define dashboard items with icons
dashboard_items = [
    {
        "id": "geometry-card",
        "title": "Location Differences",
        "description": "Analyze geographic location differences with map visualization",
        "icon": "fa-solid fa-map-location-dot",
        "image": "./assets/1.png",
        "path": "/geometry",
        "module_path": "enhanced-location-dashboard.py",  # 修改为新的文件名
        "module_name": "location_differences",  # 修改为新的模块名
        "port": 8051,
        "color": "#4361ee"  # Custom blue color
    },
    {
        "id": "response-card",
        "title": "Response Summaries",
        "description": "Response data analysis and summaries",
        "icon": "fa-solid fa-chart-column",
        "image": "./assets/2.png",
        "path": "/response",
        "module_path": "classified_response_summay.py",
        "module_name": "classified_response",
        "port": 8052,
        "color": "#38b000"  # Custom green color
    },
    {
        "id": "conceptual-card",
        "title": "Conceptual Responses",
        "description": "Conceptual classified response exploration",
        "icon": "fa-solid fa-brain",
        "image": "./assets/3.png",
        "path": "/conceptual",
        "module_path": "conceptual_classified_responses.py",
        "module_name": "conceptual_responses",
        "port": 8053,
        "color": "#8338ec"  # Custom purple color
    },
    {
        "id": "different-card",
        "title": "Different Places",
        "description": "Comparison of same ideas across different locations",
        "icon": "fa-solid fa-location-crosshairs",
        "image": "./assets/4.png",
        "path": "/different",
        "module_path": "different_place_for_sameidea_new2.py",
        "module_name": "different_place",
        "port": 8054,
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
                                        id=f"btn-{item['id']}",  # 添加ID为每个按钮
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

# 添加一个Loading组件以显示加载状态
loading_layout = dbc.Spinner(
    html.Div(
        "Loading dashboard...",
        id="loading-message",
        style={
            "textAlign": "center",
            "marginTop": "200px",
            "fontSize": "24px",
            "color": "#666"
        }
    ),
    size="lg",
    color="#4361ee",
    type="grow",
    fullscreen=True,
)

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
        # Store running sub-apps info
        dcc.Store(id="running-subapps", data={}),
        # 添加状态通知组件
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

# 用于显示状态通知的回调
@app.callback(
    [Output("status-toast", "is_open"),
     Output("status-toast", "header"),
     Output("status-toast", "children"),
     Output("status-toast", "color")],
    [Input("url", "pathname")],
    [State("running-subapps", "data")]
)
def show_status(pathname, running_subapps_data):
    if pathname == "/" or not pathname:
        return False, "", "", "primary"
    
    # 查找匹配的仪表板
    selected_dashboard = None
    for item in dashboard_items:
        if item["path"] == pathname:
            selected_dashboard = item
            break
    
    if not selected_dashboard:
        return False, "", "", "primary"
    
    # 检查子应用是否正在加载或已加载
    if selected_dashboard["path"] in running_subapps_data:
        return True, "Dashboard Ready", f"{selected_dashboard['title']} is ready.", "success"
    else:
        return True, "Loading Dashboard", f"Loading {selected_dashboard['title']}...", "primary"

# 添加加载显示回调
@app.callback(
    Output("loading-container", "children"),
    [Input("url", "pathname")],
    [State("running-subapps", "data")]
)
def show_loading(pathname, running_subapps_data):
    if pathname == "/" or not pathname:
        return ""
    
    # 查找匹配的仪表板
    selected_dashboard = None
    for item in dashboard_items:
        if item["path"] == pathname:
            selected_dashboard = item
            break
    
    if not selected_dashboard:
        return ""
    
    # 检查子应用是否已加载
    if selected_dashboard["path"] in running_subapps_data:
        return ""
    else:
        return loading_layout

# Global variable to store sub-app processes
running_subapps = {}

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

# 检查端口是否被占用
def is_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# 寻找可用端口
def find_available_port(start_port):
    port = start_port
    while is_port_in_use(port):
        port += 1
    return port

# Run sub-application in a separate thread
def run_subapp(module, port, module_name):
    try:
        # Save current working directory
        original_cwd = os.getcwd()
        
        # Change working directory to module location
        module_dir = os.path.dirname(os.path.abspath(sys.modules[module_name].__file__))
        os.chdir(module_dir)
        
        print(f"Starting sub-application {module_name} on port {port}...")
        print(f"Working directory: {os.getcwd()}")
        
        # 添加错误处理和重试机制
        try:
            # Start sub-application
            module.app.run_server(debug=False, port=port, use_reloader=False, host='127.0.0.1', dev_tools_ui=False, dev_tools_props_check=False)
        except Exception as e:
            print(f"Error starting sub-app on port {port}: {str(e)}")
            # 尝试在不同端口重启
            try:
                new_port = find_available_port(port + 100)
                print(f"Retrying on port {new_port}...")
                module.app.run_server(debug=False, port=new_port, use_reloader=False, host='127.0.0.1', dev_tools_ui=False, dev_tools_props_check=False)
            except Exception as retry_e:
                print(f"Failed to start sub-app even with new port: {str(retry_e)}")
        
        # Restore original working directory
        os.chdir(original_cwd)
    except Exception as e:
        print(f"Error running sub-application: {str(e)}\n{traceback.format_exc()}")

# Page routing callback
@app.callback(
    [Output("page-content", "children"),
     Output("home-button", "style"),
     Output("debug-info", "children"),
     Output("debug-info", "style"),
     Output("running-subapps", "data")],
    [Input("url", "pathname")],
    [State("running-subapps", "data")]
)
def display_page(pathname, running_subapps_data):
    global running_subapps
    print(f"URL path changed to: {pathname}")
    
    # Homepage
    if pathname == "/" or not pathname:
        return home_layout, {"display": "none"}, "", {"display": "none"}, running_subapps_data
    
    # Show return button
    button_style = {"display": "block", "borderRadius": "30px", "boxShadow": "0 4px 10px rgba(0,0,0,0.1)"}
    
    # Find matching dashboard
    selected_dashboard = None
    for item in dashboard_items:
        if item["path"] == pathname:
            selected_dashboard = item
            break
            
    if not selected_dashboard:
        return home_layout, {"display": "none"}, "Unknown path", {"display": "block", "padding": "10px", "background": "#f8d7da"}, running_subapps_data
    
    # 复制运行中子应用数据以进行修改
    updated_subapps_data = dict(running_subapps_data)
    
    # 检查端口是否已被占用
    base_port = selected_dashboard["port"]
    if is_port_in_use(base_port) and selected_dashboard["path"] not in running_subapps:
        # 端口被占用，寻找新端口
        port = find_available_port(base_port + 100)
        print(f"Port {base_port} is in use. Using port {port} instead.")
    else:
        port = base_port
    
    # Check if sub-app is already running
    if selected_dashboard["path"] not in running_subapps:
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
            ]), button_style, debug_msg, {"display": "block", "padding": "10px", "background": "#f8d7da"}, running_subapps_data
        
        try:
            # Start sub-app in new thread
            thread = threading.Thread(
                target=run_subapp, 
                args=(module, port, selected_dashboard["module_name"]),
                daemon=True
            )
            thread.start()
            
            # Record running sub-app
            running_subapps[selected_dashboard["path"]] = {
                "thread": thread,
                "port": port,
                "title": selected_dashboard["title"]
            }
            
            # Update stored data
            updated_subapps_data[selected_dashboard["path"]] = {
                "port": port,
                "title": selected_dashboard["title"]
            }
            
            # Give server time to start - 更合理的启动延迟
            print(f"Waiting for {selected_dashboard['title']} to start...")
            
            # 添加超时检查，确保服务器启动或超时
            max_attempts = 10
            for attempt in range(max_attempts):
                time.sleep(0.5)  # 减少每次检查的等待时间
                # 检查端口是否已经活跃
                if is_port_in_use(port):
                    print(f"{selected_dashboard['title']} started successfully on port {port}")
                    break
                print(f"Waiting... ({attempt+1}/{max_attempts})")
                if attempt == max_attempts - 1:
                    print(f"Warning: Timeout waiting for {selected_dashboard['title']} to start")
        except Exception as e:
            error_msg = f"Error starting sub-application: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            return html.Div([
                html.H4(f"Error starting {selected_dashboard['title']}"),
                html.Pre(error_msg, style={"whiteSpace": "pre-wrap", "overflow": "auto", "maxHeight": "300px"}),
                html.Div([
                    dbc.Button("Try Again", id="retry-button", color="primary", className="me-2", 
                              href=selected_dashboard["path"]),
                    dbc.Button("Return Home", href="/", color="secondary")
                ], className="mt-4 d-flex justify-content-center gap-2")
            ]), button_style, error_msg, {"display": "block", "padding": "10px", "background": "#f8d7da"}, running_subapps_data
    
    # Get sub-app port
    port = running_subapps[selected_dashboard["path"]]["port"]
    
    # Create iframe to load sub-app
    try:
        iframe_layout = html.Div([
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
            ], className="d-flex align-items-center justify-content-center"),
            # 添加错误提示和重试选项
            html.Div(
                id="iframe-error-message",
                style={"display": "none", "textAlign": "center", "margin": "20px 0", "color": "#dc3545"}
            ),
            html.Iframe(
                id="dashboard-iframe",
                src=f"http://127.0.0.1:{port}/",
                style={
                    "width": "100%", 
                    "height": "800px", 
                    "border": "none",
                    "borderRadius": "12px",
                    "boxShadow": "0 6px 18px rgba(0,0,0,0.08)"
                }
            ),
            # 添加重试按钮，仅在iframe加载失败时显示
            html.Div([
                dbc.Button("Reload Dashboard", id="reload-iframe", color="primary", className="mt-3")
            ], id="reload-container", className="text-center", style={"display": "none"})
        ])
        return iframe_layout, button_style, "", {"display": "none"}, updated_subapps_data
    except Exception as e:
        error_msg = f"Error creating interface: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return html.Div([
            html.H4(f"Error loading {selected_dashboard['title']} interface"),
            html.Pre(error_msg, style={"whiteSpace": "pre-wrap", "overflow": "auto", "maxHeight": "300px"}),
            html.Div([
                dbc.Button("Try Again", id="retry-button", color="primary", className="me-2", 
                          href=selected_dashboard["path"]),
                dbc.Button("Return Home", href="/", color="secondary")
            ], className="mt-4 d-flex justify-content-center gap-2")
        ]), button_style, error_msg, {"display": "block", "padding": "10px", "background": "#f8d7da"}, updated_subapps_data

# 添加客户端回调以检测iframe加载错误
app.clientside_callback(
    """
    function(n) {
        var iframe = document.getElementById('dashboard-iframe');
        var errorMessage = document.getElementById('iframe-error-message');
        var reloadContainer = document.getElementById('reload-container');
        
        if (iframe) {
            iframe.onerror = function() {
                if (errorMessage) {
                    errorMessage.textContent = "Failed to load dashboard. The server may not be responding.";
                    errorMessage.style.display = "block";
                }
                if (reloadContainer) {
                    reloadContainer.style.display = "block";
                    
                }
            };
            
            iframe.onload = function() {
                try {
                    // Try to access iframe content to check if it loaded properly
                    var iframeContent = iframe.contentWindow.document;
                    // If we can access content, hide error message
                    if (errorMessage) {
                        errorMessage.style.display = "none";
                    }
                    if (reloadContainer) {
                        reloadContainer.style.display = "none";
                    }
                } catch (e) {
                    // Security error or cross-origin issue
                    if (errorMessage) {
                        errorMessage.textContent = "Failed to load dashboard. The server may not be responding.";
                        errorMessage.style.display = "block"
                        }
                    if (reloadContainer) {
                        reloadContainer.style.display = "block";
                    }
                }
            };
        }
        
        return window.dash_clientside.no_update;
    }
    """,
    Output("debug-info", "data"),
    Input("url", "pathname")
)
# 添加重新加载iframe的回调
@app.callback(
    Output("dashboard-iframe", "src"),
    Input("reload-iframe", "n_clicks"),
    State("url", "pathname"),
    State("running-subapps", "data"),
    prevent_initial_call=True
)
def reload_iframe(n_clicks, pathname, running_subapps_data):
    if not n_clicks:
        return dash.no_update
    
    # 查找匹配的仪表板和端口
    for item in dashboard_items:
        if item["path"] == pathname and pathname in running_subapps_data:
            port = running_subapps_data[pathname]["port"]
            # 添加时间戳以避免缓存
            timestamp = int(time.time())
            return f"http://127.0.0.1:{port}/?t={timestamp}"
    
    # 如果找不到匹配的仪表板，返回当前src
    return dash.no_update

if __name__ == "__main__":
    # Create assets directory
    if not os.path.exists("assets"):
        os.makedirs("assets")
    
    # Create custom CSS file with enhanced styles
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
        """)
    
    # 修改：只有在环境变量中指定时才自动打开浏览器    
    def open_browser():
        global browser_opened
        if not browser_opened:
            browser_opened = True
            time.sleep(1)
            webbrowser.open("http://127.0.0.1:8050")
    
    # 仅当此脚本直接运行时打开浏览器，而不是被其他脚本导入时
    if os.environ.get('OPEN_BROWSER', '0') == '1':
        threading.Thread(target=open_browser, daemon=True).start()
    
    # Start server
    print("Starting dashboard application...")
    app.run_server(debug=False, port=8050, use_reloader=False)
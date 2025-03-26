"""
Conceptual Classified Responses Module
------------------------------------
This module provides the layout and callbacks for the Conceptual Classified Responses dashboard
"""

from dash import html, dcc, Input, Output, State, callback
import pandas as pd
import json
import dash
from urllib.parse import parse_qs, unquote, quote

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

# Load data function
def load_data():
    try:
        df = pd.read_csv("./conceptual_classified_responses.csv")
    except:
        # If file doesn't exist, create empty dataframe with appropriate columns
        df = pd.DataFrame(columns=['Open Location Code', 'Category', 'Idea Number', 'Response', 'Upvotes', 'Downvotes'])
    
    # Process main table: deduplicate Open Location Code + Category
    df_main = df[['Open Location Code', 'Category']].drop_duplicates().reset_index(drop=True)
    
    # Calculate rowspan for merging cells
    df_main["RowSpan"] = df_main.groupby("Open Location Code")["Category"].transform("count")
    
    return df, df_main

# Main layout generator
def get_main_layout():
    return html.Div([
        html.H1("Conceptual Classified Responses", style={'textAlign': 'center'}),

        # Add search box
        html.Div([
            html.Label("Search Open Location Code:"),
            dcc.Input(
                id="concept-search-input",
                type="text",
                placeholder="Enter Open Location Code...",
                style={'marginLeft': '10px', 'padding': '5px', 'width': '300px'}
            ),
            html.Button(
                "Search",
                id="concept-search-button",
                style={
                    'marginLeft': '10px',
                    'padding': '5px 15px',
                    'backgroundColor': '#4CAF50',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '4px',
                    'cursor': 'pointer'
                }
            )
        ], style={'margin': '20px 0', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}),

        html.Div(id="concept-main-table-div", children=[
            html.Table(
                id="concept-main-table",
                style={'width': '100%', 'borderCollapse': 'collapse'},
                children=[
                    html.Thead(
                        html.Tr([
                            html.Th("Open Location Code", style=header_style),
                            html.Th("Category", style=header_style)
                        ])
                    ),
                    html.Tbody(id="concept-table-body")
                ]
            )
        ])
    ])

# Detail page layout
def get_detail_layout(olc=None, category=None):
    # Handle case where parameters are not provided
    if not olc or not category:
        return html.Div([
            html.Button(
                "🔙 Back to Dashboard",
                id="concept-back-to-main-btn",
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
            html.H3("Please select an Open Location Code and Category from the main page", 
                   style={'textAlign': 'center', 'marginTop': '50px', 'color': '#666'})
        ])
    
    df, _ = load_data()
    filtered_df = df[(df["Open Location Code"] == olc) & (df["Category"] == category)]
    
    if filtered_df.empty:
        return html.Div([
            html.Button(
                "🔙 Back to Dashboard",
                id="concept-back-to-main-btn",
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
            html.H3(f"No data found for {olc} - {category}", 
                   style={'textAlign': 'center', 'marginTop': '50px', 'color': '#666'})
        ])
    
    # Generate detail rows
    rows = []
    category_span = len(filtered_df)

    for i, (_, row) in enumerate(filtered_df.iterrows()):
        if i == 0:
            # First row needs to include Category with rowSpan
            tr = html.Tr([
                html.Td(
                    category,
                    rowSpan=category_span,
                    style={
                        'textAlign': 'center',
                        'verticalAlign': 'middle',
                        'border': '1px solid #ddd',
                        'padding': '10px',
                        'backgroundColor': '#f9f9f9'
                    }
                ),
                html.Td(row["Idea Number"], style={
                    'border': '1px solid #ddd',
                    'padding': '10px',
                    'textAlign': 'center'
                }),
                html.Td(row["Response"], style={
                    'border': '1px solid #ddd',
                    'padding': '10px',
                    'textAlign': 'left'
                }),
                html.Td(row["Upvotes"], style={
                    'border': '1px solid #ddd',
                    'padding': '10px',
                    'textAlign': 'center'
                }),
                html.Td(row["Downvotes"], style={
                    'border': '1px solid #ddd',
                    'padding': '10px',
                    'textAlign': 'center'
                })
            ])
        else:
            # Subsequent rows don't include Category
            tr = html.Tr([
                html.Td(row["Idea Number"], style={
                    'border': '1px solid #ddd',
                    'padding': '10px',
                    'textAlign': 'center'
                }),
                html.Td(row["Response"], style={
                    'border': '1px solid #ddd',
                    'padding': '10px',
                    'textAlign': 'left'
                }),
                html.Td(row["Upvotes"], style={
                    'border': '1px solid #ddd',
                    'padding': '10px',
                    'textAlign': 'center'
                }),
                html.Td(row["Downvotes"], style={
                    'border': '1px solid #ddd',
                    'padding': '10px',
                    'textAlign': 'center'
                })
            ])

        rows.append(tr)

    return html.Div([
        html.Button(
            "🔙 Back",
            id="concept-back-to-main-btn",
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
        html.H2(f"Location: {olc}", style={'textAlign': 'center'}),

        # Use custom HTML table to implement merged cells
        html.Table(
            style={
                'width': '100%',
                'borderCollapse': 'collapse',
                'marginTop': '20px'
            },
            children=[
                html.Thead(
                    html.Tr([
                        html.Th("Category", style=header_style),
                        html.Th("Idea Number", style=header_style),
                        html.Th("Response", style=header_style),
                        html.Th("Upvotes", style=header_style),
                        html.Th("Downvotes", style=header_style)
                    ])
                ),
                html.Tbody(rows)
            ]
        )
    ])

# Register all callbacks for this module
def register_callbacks(app):
    @app.callback(
        Output("concept-table-body", "children"),
        [Input("concept-search-button", "n_clicks")],
        [State("concept-search-input", "value")]
    )
    def update_table_body(search_clicks, search_value):
        _, df_main = load_data()
        
        # Filter based on search value
        filtered_df_main = df_main
        if search_value:
            filtered_df_main = df_main[df_main["Open Location Code"].str.contains(search_value, case=False)]

        rows = []
        current_olc = None
        rowspan_count = 0

        for index, row in filtered_df_main.iterrows():
            olc = row["Open Location Code"]
            category = row["Category"]

            if olc != current_olc:
                current_olc = olc
                # Recalculate rowspan for filtered data
                rowspan_count = len(filtered_df_main[filtered_df_main["Open Location Code"] == olc])
                tr = html.Tr([
                    html.Td(
                        olc,
                        rowSpan=rowspan_count,
                        style={
                            'textAlign': 'center',
                            'verticalAlign': 'middle',
                            'border': '1px solid #ddd',
                            'padding': '10px'
                        }
                    ),
                    html.Td(
                        html.Button(
                            category,
                            id={"type": "concept-category-button", "index": index, "olc": olc, "category": category},
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
                                'textDecoration': 'none'
                            }
                        ),
                        style={
                            'border': '1px solid #ddd',
                            'padding': '0'
                        }
                    )
                ])
            else:
                tr = html.Tr(
                    html.Td(
                        html.Button(
                            category,
                            id={"type": "concept-category-button", "index": index, "olc": olc, "category": category},
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
                                'textDecoration': 'none'
                            }
                        ),
                        style={
                            'border': '1px solid #ddd',
                            'padding': '0'
                        }
                    )
                )
            rows.append(tr)

        if not rows:
            rows = [
                html.Tr(html.Td("No matching records found", colSpan=2, style={'textAlign': 'center', 'padding': '20px'}))]

        return rows
    
    @app.callback(
        Output("concept-state", "data"),
        [Input({"type": "concept-category-button", "index": dash.ALL, "olc": dash.ALL, "category": dash.ALL}, "n_clicks"),
         Input("concept-back-to-main-btn", "n_clicks")],
        [State("concept-state", "data")]
    )
    def update_page_state(category_clicks, back_clicks, current_state):
        ctx = dash.callback_context
        
        if not ctx.triggered:
            return current_state
            
        # Get the ID of the component that triggered the callback
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Handle back button
        if trigger_id == "concept-back-to-main-btn":
            return {'view': 'main', 'olc': None, 'category': None}
            
        # Handle category selection
        try:
            trigger = json.loads(trigger_id)
            if trigger.get('type') == 'concept-category-button':
                return {
                    'view': 'detail',
                    'olc': trigger.get('olc'),
                    'category': trigger.get('category')
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
        dcc.Store(id="concept-state", data={'view': 'main', 'olc': None, 'category': None}),
        html.Div(id='concept-page-content')
    ])

# Handle page content based on state
@callback(
    Output('concept-page-content', 'children'),
    [Input('concept-state', 'data')])
def render_page_content(state):
    view = state.get('view', 'main')
    
    if view == 'main':
        return get_main_layout()
    elif view == 'detail':
        return get_detail_layout(state.get('olc'), state.get('category'))
    else:
        return get_main_layout()

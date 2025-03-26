"""
Response Summaries Module
------------------------
This module provides the layout and callbacks for the Response Summaries dashboard
"""

from dash import html, dcc, Input, Output, State, callback
import pandas as pd
import json
import dash
from urllib.parse import parse_qs, unquote, quote

# Style definitions
header_style = {
    'backgroundColor': '#f8f9fa',
    'padding': '12px',
    'border': '1px solid #ddd',
    'textAlign': 'center',
    'fontWeight': 'bold'
}

cell_style = {
    'border': '1px solid #ddd',
    'padding': '10px',
    'textAlign': 'left',
    'verticalAlign': 'middle'
}

# Load data function
def load_data():
    try:
        df = pd.read_csv("./classified_response_summaries2.csv")
    except:
        # If file doesn't exist, create empty dataframe with appropriate columns
        df = pd.DataFrame(columns=['Category', 'Groups', 'Summary', 'Response', 'Upvotes', 'Downvotes'])
    
    # Process main table: deduplicate Category + Groups
    df_main = df[['Category', 'Groups']].drop_duplicates().reset_index(drop=True)
    df_main["RowSpan"] = df_main.groupby("Category")["Groups"].transform("count")
    
    return df, df_main

# Main layout generator
def get_main_layout():
    return html.Div([
        html.H1("Response Summary Dashboard", style={'textAlign': 'center', 'margin': '20px'}),
        html.Div([
            html.Table(
                id="resp-main-table",
                style={'width': '80%', 'margin': 'auto', 'borderCollapse': 'collapse', 'border': '1px solid #ddd'},
                children=[
                    html.Thead(html.Tr([
                        html.Th("Category",
                                style={'backgroundColor': '#f8f9fa', 'padding': '12px', 'border': '1px solid #ddd',
                                       'textAlign': 'center'}),
                        html.Th("Groups",
                                style={'backgroundColor': '#f8f9fa', 'padding': '12px', 'border': '1px solid #ddd',
                                       'textAlign': 'left'})
                    ])),
                    html.Tbody(id="resp-table-body")
                ]
            )
        ])
    ])

# Detail page layout
def get_detail_layout(category=None, group=None):
    # Handle case where parameters are not provided
    if not category or not group:
        return html.Div([
            html.Button(
                "🔙 Back to Dashboard",
                id="resp-back-to-main-btn",
                style={
                    'margin': '20px',
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
    filtered_df = df[(df["Category"] == category) & (df["Groups"] == group)].sort_values('Upvotes', ascending=False)
    
    if filtered_df.empty:
        return html.Div([
            html.Button(
                "🔙 Back to Dashboard",
                id="resp-back-to-main-btn",
                style={
                    'margin': '20px',
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
    
    # Process data for display with merged cells
    summary_counts = filtered_df.groupby("Summary").size().reset_index(name='Count')
    merged_data = pd.merge(filtered_df, summary_counts, on="Summary")

    rows = []
    current_summary = None
    
    for index, row in merged_data.iterrows():
        if row["Summary"] != current_summary:
            current_summary = row["Summary"]
            rowspan = row["Count"]
            rows.append(html.Tr([
                html.Td(current_summary, rowSpan=rowspan,
                        style={'textAlign': 'center', 'verticalAlign': 'middle', 'border': '1px solid #ddd',
                               'padding': '10px', 'backgroundColor': '#f8f9fa'}),
                html.Td(row["Response"], style={'border': '1px solid #ddd', 'padding': '10px'}),
                html.Td(row["Upvotes"], style={'border': '1px solid #ddd', 'padding': '10px', 'textAlign': 'center',
                                               'color': '#28a745'}),
                html.Td(row["Downvotes"], style={'border': '1px solid #ddd', 'padding': '10px', 'textAlign': 'center',
                                                 'color': '#dc3545'})
            ]))
        else:
            rows.append(html.Tr([
                html.Td(row["Response"], style={'border': '1px solid #ddd', 'padding': '10px'}),
                html.Td(row["Upvotes"], style={'border': '1px solid #ddd', 'padding': '10px', 'textAlign': 'center',
                                               'color': '#28a745'}),
                html.Td(row["Downvotes"], style={'border': '1px solid #ddd', 'padding': '10px', 'textAlign': 'center',
                                                 'color': '#dc3545'})
            ]))
    
    return html.Div([
        html.Button(
            "🔙 Back to Main",
            id="resp-back-to-main-btn",
            style={
                'display': 'block', 
                'margin': '20px', 
                'padding': '8px 16px',
                'backgroundColor': '#007bff',
                'color': 'white',
                'borderRadius': '4px',
                'border': 'none',
                'cursor': 'pointer',
                'fontWeight': 'bold'
            }
        ),
        html.H2(f"Details for {category} - {group}", style={'textAlign': 'center'}),
        html.Div(
            html.Table(
                style={'width': '80%', 'margin': 'auto', 'borderCollapse': 'collapse', 'border': '1px solid #ddd'},
                children=[
                    html.Thead(html.Tr([
                        html.Th("Summary", style={'width': '20%', 'backgroundColor': '#e9ecef', 'padding': '12px'}),
                        html.Th("Response", style={'width': '50%', 'backgroundColor': '#e9ecef', 'padding': '12px'}),
                        html.Th("Upvotes ▼", style={'width': '15%', 'backgroundColor': '#e9ecef', 'padding': '12px'}),
                        html.Th("Downvotes", style={'width': '15%', 'backgroundColor': '#e9ecef', 'padding': '12px'})
                    ])),
                    html.Tbody(rows)
                ]
            ),
            style={'marginBottom': '50px'}
        )
    ])

# Register all callbacks for this module
def register_callbacks(app):
    @app.callback(
        Output("resp-table-body", "children"),
        [Input("url", "pathname")]
    )
    def update_table_body(_):
        _, df_main = load_data()
        rows = []
        current_category = None
        
        for index, row in df_main.iterrows():
            category, group = row["Category"], row["Groups"]
            if category != current_category:
                current_category = category
                rowspan = int(row["RowSpan"])
                rows.append(html.Tr([
                    html.Td(category, rowSpan=rowspan,
                            style={'textAlign': 'center', 'verticalAlign': 'middle', 'padding': '12px',
                                   'border': '1px solid #ddd', 'backgroundColor': '#f8f9fa'}),
                    html.Td(
                        html.Button(
                            group,
                            id={"type": "group-button", "index": index, "category": category, "group": group},
                            style={
                                'width': '100%',
                                'textAlign': 'left',
                                'backgroundColor': 'transparent',
                                'border': 'none',
                                'cursor': 'pointer',
                                'fontFamily': 'inherit',
                                'fontSize': 'inherit',
                                'padding': '10px',
                                'color': '#007bff',
                                'textDecoration': 'none',
                                'display': 'block'
                            }
                        ),
                        style={'border': '1px solid #ddd'}
                    )
                ]))
            else:
                rows.append(html.Tr([
                    html.Td(
                        html.Button(
                            group,
                            id={"type": "group-button", "index": index, "category": category, "group": group},
                            style={
                                'width': '100%',
                                'textAlign': 'left',
                                'backgroundColor': 'transparent',
                                'border': 'none',
                                'cursor': 'pointer',
                                'fontFamily': 'inherit',
                                'fontSize': 'inherit',
                                'padding': '10px',
                                'color': '#007bff',
                                'textDecoration': 'none',
                                'display': 'block'
                            }
                        ),
                        style={'border': '1px solid #ddd'}
                    )
                ]))
        
        if not rows:
            rows = [html.Tr(html.Td("No data available", colSpan=2, 
                                    style={'textAlign': 'center', 'padding': '20px'}))]
        
        return rows
    
    @app.callback(
        Output("resp-state", "data"),
        [Input({"type": "group-button", "index": dash.ALL, "category": dash.ALL, "group": dash.ALL}, "n_clicks"),
         Input("resp-back-to-main-btn", "n_clicks")],
        [State("resp-state", "data")]
    )
    def update_page_state(group_clicks, back_clicks, current_state):
        ctx = dash.callback_context
        
        if not ctx.triggered:
            return current_state
            
        # Get the ID of the component that triggered the callback
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Handle back button
        if trigger_id == "resp-back-to-main-btn":
            return {'view': 'main', 'category': None, 'group': None}
            
        # Handle group selection
        try:
            trigger = json.loads(trigger_id)
            if trigger.get('type') == 'group-button':
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
        dcc.Store(id="resp-state", data={'view': 'main', 'category': None, 'group': None}),
        html.Div(id='resp-page-content')
    ])

# Handle page content based on state
@callback(
    Output('resp-page-content', 'children'),
    [Input('resp-state', 'data')])
def render_page_content(state):
    view = state.get('view', 'main')
    
    if view == 'main':
        return get_main_layout()
    elif view == 'detail':
        return get_detail_layout(state.get('category'), state.get('group'))
    else:
        return get_main_layout()

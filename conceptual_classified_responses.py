from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
from urllib.parse import parse_qs, unquote, quote

# 读取数据
df = pd.read_csv("./conceptual_classified_responses.csv")

# 处理主表：去重 Open Location Code + Category
df_main = df[['Open Location Code', 'Category']].drop_duplicates().reset_index(drop=True)

# 计算每个 Open Location Code 的出现次数，用于合并单元格
df_main["RowSpan"] = df_main.groupby("Open Location Code")["Category"].transform("count")

# 初始化 Dash
app = Dash(__name__)
app.config.suppress_callback_exceptions = True  # 允许动态布局

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# 主页面布局
main_layout = html.Div([
    html.H1("Conceptual Classified Responses", style={'textAlign': 'center'}),

    # 添加搜索框（居中放置）
    html.Div([
        html.Label("Search Open Location Code:"),
        dcc.Input(
            id="search-input",
            type="text",
            placeholder="Enter Open Location Code...",
            style={'marginLeft': '10px', 'padding': '5px', 'width': '300px'}
        ),
        html.Button(
            "Search",
            id="search-button",
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

    html.Div(id="main_table_div", children=[
        html.Table(
            id="main_table",
            style={'width': '100%', 'borderCollapse': 'collapse'},
            children=[
                html.Thead(
                    html.Tr([
                        html.Th("Open Location Code", style={
                            'backgroundColor': 'lightgrey',
                            'fontWeight': 'bold',
                            'padding': '10px',
                            'textAlign': 'center',
                            'border': '1px solid #ddd'
                        }),
                        html.Th("Category", style={
                            'backgroundColor': 'lightgrey',
                            'fontWeight': 'bold',
                            'padding': '10px',
                            'textAlign': 'left',
                            'border': '1px solid #ddd'
                        })
                    ])
                ),
                html.Tbody(id="table_body")
            ]
        )
    ])
])


# 详情页面布局
def detail_layout(olc, category):
    filtered_df = df[(df["Open Location Code"] == olc) & (df["Category"] == category)]

    # 创建一个对Idea Number进行分组的数据结构，用于合并Category单元格
    idea_groups = filtered_df.groupby("Idea Number")
    idea_counts = idea_groups.size().reset_index(name='count')

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
        html.H2(f"Location: {olc}", style={'textAlign': 'center'}),

        # 使用自定义HTML表格来实现合并单元格
        html.Table(
            style={
                'width': '100%',
                'borderCollapse': 'collapse',
                'marginTop': '20px'
            },
            children=[
                html.Thead(
                    html.Tr([
                        html.Th("Category", style={
                            'backgroundColor': 'lightgrey',
                            'fontWeight': 'bold',
                            'padding': '10px',
                            'textAlign': 'center',
                            'border': '1px solid #ddd'
                        }),
                        html.Th("Idea Number", style={
                            'backgroundColor': 'lightgrey',
                            'fontWeight': 'bold',
                            'padding': '10px',
                            'textAlign': 'center',
                            'border': '1px solid #ddd'
                        }),
                        html.Th("Response", style={
                            'backgroundColor': 'lightgrey',
                            'fontWeight': 'bold',
                            'padding': '10px',
                            'textAlign': 'center',
                            'border': '1px solid #ddd'
                        }),
                        html.Th("Upvotes", style={
                            'backgroundColor': 'lightgrey',
                            'fontWeight': 'bold',
                            'padding': '10px',
                            'textAlign': 'center',
                            'border': '1px solid #ddd'
                        }),
                        html.Th("Downvotes", style={
                            'backgroundColor': 'lightgrey',
                            'fontWeight': 'bold',
                            'padding': '10px',
                            'textAlign': 'center',
                            'border': '1px solid #ddd'
                        })
                    ])
                ),
                html.Tbody(id="detail_table_body", children=generate_detail_rows(filtered_df, category))
            ]
        )
    ])


# 生成详情表格行的函数
def generate_detail_rows(filtered_df, category):
    rows = []
    category_span = len(filtered_df)

    for i, (_, row) in enumerate(filtered_df.iterrows()):
        if i == 0:
            # 第一行需要包含Category并设置rowSpan
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
            # 后续行不包含Category
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

    return rows


# 页面路由回调
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'),
     Input('url', 'search')]
)
def display_page(pathname, search):
    if pathname == '/detail':
        params = parse_qs(search.lstrip('?'))
        olc = unquote(params.get('olc', [None])[0])
        category = unquote(params.get('category', [None])[0])

        if not olc or not category:
            return html.Div("Missing parameters")

        return detail_layout(olc, category)
    else:
        return main_layout


# 生成主表内容回调
@app.callback(
    Output("table_body", "children"),
    [Input('url', 'pathname'),
     Input("search-button", "n_clicks")],
    [State("search-input", "value")]
)
def update_table_body(_, search_clicks, search_value):
    # 基于搜索值筛选数据
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
            # 由于过滤了数据，我们需要重新计算同一OLC的出现次数
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
                    dcc.Link(
                        category,
                        href=f"/detail?olc={quote(olc)}&category={quote(category)}",
                        target="_blank",
                        style={'textDecoration': 'none', 'color': '#0066cc'}
                    ),
                    style={
                        'border': '1px solid #ddd',
                        'padding': '10px'
                    }
                )
            ])
        else:
            tr = html.Tr(
                html.Td(
                    dcc.Link(
                        category,
                        href=f"/detail?olc={quote(olc)}&category={quote(category)}",
                        target="_blank",
                        style={'textDecoration': 'none', 'color': '#0066cc'}
                    ),
                    style={
                        'border': '1px solid #ddd',
                        'padding': '10px'
                    }
                )
            )
        rows.append(tr)

    if not rows:
        rows = [
            html.Tr(html.Td("No matching records found", colSpan=2, style={'textAlign': 'center', 'padding': '20px'}))]

    return rows


if __name__ == "__main__":
    import dash

    app.run_server(debug=True)
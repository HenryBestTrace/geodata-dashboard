from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import pandas as pd
from urllib.parse import parse_qs, unquote, quote

# 读取数据
df = pd.read_csv("./classified_response_summaries2.csv")

# 处理主表：去重 Category + Groups
df_main = df[['Category', 'Groups']].drop_duplicates().reset_index(drop=True)
df_main["RowSpan"] = df_main.groupby("Category")["Groups"].transform("count")

# 初始化 Dash
app = Dash(__name__)
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# 主页面布局（关键修改点：添加 target="_blank"）
main_layout = html.Div([
    html.H1("Response Summary Dashboard", style={'textAlign': 'center', 'margin': '20px'}),
    html.Div([
        html.Table(
            id="main_table",
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
                html.Tbody(id="table_body")
            ]
        )
    ])
])


# 详情页面布局（保持不变）
def detail_layout(category, group):
    filtered_df = df[(df["Category"] == category) & (df["Groups"] == group)].sort_values('Upvotes', ascending=False)
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
        dcc.Link("🔙 Back to Main", href="/",
                 style={'display': 'block', 'margin': '20px', 'color': '#007bff', 'textDecoration': 'none',
                        'fontWeight': 'bold'}),
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


# 路由回调（保持不变）
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'), Input('url', 'search')]
)
def display_page(pathname, search):
    if pathname == '/detail':
        params = parse_qs(search.lstrip('?'))
        category = unquote(params.get('category', [None])[0])
        group = unquote(params.get('group', [None])[0])
        return detail_layout(category, group) if category and group else html.Div("Invalid Request")
    return main_layout


# 生成主表内容（关键修改点：添加 target="_blank"）
@app.callback(
    Output("table_body", "children"),
    [Input('url', 'pathname')]
)
def update_table_body(_):
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
                    dcc.Link(
                        group,
                        href=f"/detail?category={quote(category)}&group={quote(group)}",
                        target="_blank",  # 新增此行实现新标签页打开
                        style={'color': '#007bff', 'textDecoration': 'none', 'display': 'block', 'padding': '10px'}
                    ),
                    style={'border': '1px solid #ddd'}
                )
            ]))
        else:
            rows.append(html.Tr([
                html.Td(
                    dcc.Link(
                        group,
                        href=f"/detail?category={quote(category)}&group={quote(group)}",
                        target="_blank",  # 新增此行
                        style={'color': '#007bff', 'textDecoration': 'none', 'display': 'block', 'padding': '10px'}
                    ),
                    style={'border': '1px solid #ddd'}
                )
            ]))
    return rows


if __name__ == "__main__":
    app.run_server(debug=True)
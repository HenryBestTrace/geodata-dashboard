from dash import Dash, dcc, html, dash_table, ALL, callback_context, Input, Output, State
import pandas as pd
from urllib.parse import parse_qs, unquote, quote
from shapely import wkt
import plotly.graph_objects as go
import plotly.express as px
import json

df = pd.read_csv('./different_place_for_sameidea2.csv')
df_main = df[['Category', 'Groups']].drop_duplicates().reset_index(drop=True)
df_main["RowSpan"] = df_main.groupby("Category")["Groups"].transform("count")

# %%
# 样式定义
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


# 地图生成函数
def create_enhanced_map(geometry_data, selected_row_data):
    fig = go.Figure()
    colors = px.colors.qualitative.Plotly
    all_coords = []

    for idx, data in enumerate(geometry_data):
        geom_str = data['geometry']
        olc = data['olc']

        try:
            geom = wkt.loads(geom_str)
            print(f"Processing {geom.geom_type} with OLC: {olc}")  # 调试输出

            if geom.geom_type in ['Polygon', 'LineString']:
                # 统一坐标提取方式
                if geom.geom_type == 'Polygon':
                    coords = list(geom.exterior.coords)
                else:  # LineString
                    coords = list(geom.coords)

                lons = [x for x, y in coords]
                lats = [y for x, y in coords]

                # 确保坐标有效性
                if not all(-180 <= lon <= 180 for lon in lons):
                    print(f"Invalid longitude in {olc}")
                if not all(-90 <= lat <= 90 for lat in lats):
                    print(f"Invalid latitude in {olc}")

                color = colors[idx % len(colors)]

                # 创建填充颜色（与线条相同但有透明度）
                if color.startswith('#'):
                    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                    fill_color = f"rgba({r}, {g}, {b}, 0.3)"
                else:
                    # 尝试从rgb格式转换
                    fill_color = color.replace('rgb', 'rgba').replace(')', ', 0.3)')

                # 设置填充条件
                is_selected = selected_row_data and selected_row_data[0]['OLCs'] == olc
                fill = "toself" if geom.geom_type == 'Polygon' else None

                # 使用lines+markers模式，但将markers的大小设为极小
                fig.add_trace(go.Scattermapbox(
                    mode='lines+markers',  # 保留标记但使其非常小
                    lon=lons,
                    lat=lats,
                    line=dict(width=3, color=color),  # 调整线宽
                    marker=dict(size=2, color=color),  # 使标记点非常小
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
        # 计算坐标范围
        lons = [x for x, y in all_coords]
        lats = [y for x, y in all_coords]
        center_lon = sum(lons) / len(lons)
        center_lat = sum(lats) / len(lats)

        zoom = 16  # 根据实际情况调整

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


# 初始化Dash应用
app = Dash(__name__)
app.config.suppress_callback_exceptions = True

# 主页面布局（保持不变）
main_layout = html.Div([
    html.H1("Conceptual Classified Responses", style={'textAlign': 'center'}),
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
                html.Tbody(id="table-body")
            ]
        )
    )
])


# 修改详情页面布局，使用HTML表格而不是DataTable来实现真正的单元格合并
def detail_layout(category, group):
    filtered_df = df[(df["Category"] == category) & (df["Groups"] == group)]

    # 提取唯一值
    group_value = filtered_df['Groups'].iloc[0] if not filtered_df.empty else ""
    summary_value = filtered_df['Summary'].iloc[0] if not filtered_df.empty else ""
    keywords_value = filtered_df['Keywords'].iloc[0] if not filtered_df.empty else ""

    # 行数
    num_rows = len(filtered_df)

    # 准备地图数据
    geometry_data = filtered_df[['geometry', 'OLCs']] \
        .rename(columns={'OLCs': 'olc'}).to_dict('records')

    # 创建OLC单元格，每个单元格都有一个点击事件
    olc_cells = []
    for i in range(num_rows):
        olc_value = filtered_df['OLCs'].iloc[i] if i < len(filtered_df) else ""
        # 为每个OLC单元格创建一个可点击的div
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

    # 创建几何单元格
    geometry_cells = []
    for i in range(num_rows):
        geom_value = filtered_df['geometry'].iloc[i] if i < len(filtered_df) else ""
        geom_cell = html.Td(geom_value, style=cell_style)
        geometry_cells.append(geom_cell)

    # 创建表格行
    table_rows = []

    # 第一行包含合并的单元格
    first_row = html.Tr([
        # 合并单元格 - Groups
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
        # 合并单元格 - Summary
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
        # 合并单元格 - Keywords
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
        # 第一行的OLCs和Geometry
        olc_cells[0] if olc_cells else html.Td("", style=cell_style),
        geometry_cells[0] if geometry_cells else html.Td("", style=cell_style)
    ])
    table_rows.append(first_row)

    # 添加剩余行
    for i in range(1, num_rows):
        row = html.Tr([
            olc_cells[i] if i < len(olc_cells) else html.Td("", style=cell_style),
            geometry_cells[i] if i < len(geometry_cells) else html.Td("", style=cell_style)
        ])
        table_rows.append(row)

    return html.Div([
        html.Div(
            dcc.Link(
                "🔙 Back to Main",
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
            )
        ),
        # 使用HTML表格实现真正的单元格合并
        html.Div(
            html.Table(
                style={'width': '100%', 'borderCollapse': 'collapse', 'margin': '20px'},
                children=[
                    # 表头
                    html.Thead(
                        html.Tr([
                            html.Th("Groups", style=header_style),
                            html.Th("Summary", style=header_style),
                            html.Th("Keywords", style=header_style),
                            html.Th("OLCs", style=header_style),
                            html.Th("Geometry", style=header_style),
                        ])
                    ),
                    # 表体
                    html.Tbody(table_rows)
                ]
            )
        ),

        # 存储选中的OLC
        dcc.Store(id='selected-row-data', data=[]),

        # 地图显示
        dcc.Graph(
            id='geometry-map',
            figure=create_enhanced_map(geometry_data, []),
            style=map_style
        )
    ])


# 回调函数
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'),
     Input('url', 'search')]
)
def display_page(pathname, search):
    if pathname == '/detail':
        params = parse_qs(search.lstrip('?'))
        category = unquote(params.get('category', [None])[0])
        group = unquote(params.get('group', [None])[0])
        return detail_layout(category, group) if category and group else main_layout
    return main_layout


@app.callback(
    Output("table-body", "children"),
    [Input('url', 'pathname')]
)
def update_table_body(_):
    rows = []
    current_category = None

    for _, row in df_main.iterrows():
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
                    dcc.Link(
                        group,
                        href=f"/detail?category={quote(category)}&group={quote(group)}",
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
                        group,
                        href=f"/detail?category={quote(category)}&group={quote(group)}",
                        target="_blank",
                        style=link_style
                    ),
                    style=cell_style
                )
            ]))
    return rows


# 处理OLC按钮点击事件
@app.callback(
    Output('selected-row-data', 'data'),
    [Input({'type': 'olc-button', 'index': ALL}, 'n_clicks')],
    [State('url', 'search')]
)
def handle_olc_button_click(n_clicks, search):
    ctx = callback_context
    if not ctx.triggered or not any(n_clicks):
        return []

    # 获取被点击的按钮ID
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if not button_id:
        return []

    try:
        # 解析按钮索引
        button_id_dict = json.loads(button_id)
        button_index = button_id_dict.get('index', 0)

        # 获取当前类别和组
        params = parse_qs(search.lstrip('?'))
        category = unquote(params.get('category', [None])[0])
        group = unquote(params.get('group', [None])[0])

        if category and group:
            filtered_df = df[(df["Category"] == category) & (df["Groups"] == group)]
            if button_index < len(filtered_df):
                selected_row = filtered_df.iloc[button_index]
                return [{'OLCs': selected_row['OLCs']}]
    except Exception as e:
        print(f"Error handling button click: {str(e)}")

    return []


# 更新地图回调函数
@app.callback(
    Output('geometry-map', 'figure'),
    [Input('selected-row-data', 'data'),
     Input('url', 'search')]
)
def update_map(selected_row_data, search):
    params = parse_qs(search.lstrip('?'))
    category = unquote(params.get('category', [None])[0])
    group = unquote(params.get('group', [None])[0])

    if category and group:
        filtered_df = df[(df["Category"] == category) & (df["Groups"] == group)]
        geometry_data = filtered_df[['geometry', 'OLCs']] \
            .rename(columns={'OLCs': 'olc'}).to_dict('records')
        return create_enhanced_map(geometry_data, selected_row_data)
    return go.Figure()  # 返回空图


# 应用配置
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
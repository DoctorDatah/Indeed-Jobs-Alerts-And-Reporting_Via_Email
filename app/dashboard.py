import os
import logging
import pandas as pd
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
from datetime import datetime, timedelta  # Ensure timedelta is imported
import reporting.raw_data_reporting   

# Set up logging
logging.basicConfig(level=logging.INFO)

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
working_dir = os.path.abspath(os.path.join(script_dir, '..'))
os.chdir(working_dir)
logging.info(f"Working directory set to: {working_dir}")

# Global file paths
intermediate_data_dir = os.path.join(working_dir, 'data', 'intermediate')
raw_data_dir = os.path.join(working_dir, 'data', 'raw')


class Dashboard:
    @staticmethod
    def create_app():
        """Create a Dash app with horizontal menus and a refresh button."""
        app = dash.Dash(__name__, suppress_callback_exceptions=True)

        app.layout = html.Div([
            html.H1("Indeed Email Jobs Alerts Dashboard", style={'textAlign': 'center', 'marginBottom': '20px'}),
            html.H2("Developed by Malik Hassan Qayyum", style={'textAlign': 'center', 'marginBottom': '30px', 'color': '#555'}),

            # Refresh Button
            html.Div([
                html.Button("Refresh Data", id="refresh-button", n_clicks=0, style={'marginRight': '10px'}),
                html.Span(id="refresh-status", style={'fontSize': '14px', 'color': '#555'}),
            ], style={'marginBottom': '20px'}),

            # Dropdown Filters
            html.Div([
                html.Div([
                    dcc.Dropdown(id='company-filter', placeholder='Select Company', multi=True)
                ], style={'width': '30%', 'display': 'inline-block', 'paddingRight': '10px'}),
                html.Div([
                    dcc.Dropdown(id='location-filter', placeholder='Select Location', multi=True)
                ], style={'width': '30%', 'display': 'inline-block', 'paddingRight': '10px'}),
                html.Div([
                    dcc.Dropdown(id='type-filter', placeholder='Select Type', multi=True)
                ], style={'width': '30%', 'display': 'inline-block'})
            ], style={'marginBottom': '20px'}),

            # Horizontal Menu
            dcc.Tabs(id='menu-tabs', value='menu-1', children=[
                dcc.Tab(label='Menu 1: Pure CSV', value='menu-1'),
                dcc.Tab(label='Menu 2: Grouped', value='menu-2'),
                dcc.Tab(label='Menu 3: Most Recent', value='menu-3')
            ]),

            # Content for each menu
            html.Div(id='menu-tabs-content', style={'marginTop': '20px'})
        ])

        @app.callback(
            [Output('company-filter', 'options'),
             Output('location-filter', 'options'),
             Output('type-filter', 'options')],
            [Input('refresh-button', 'n_clicks')]
        )
        def update_filters(n_clicks):
            intermediate_data = reporting.raw_data_reporting.intermediate_load_data(intermediate_data_dir, top_n=None)
            company_options = [{'label': company[:40], 'value': company} for company in intermediate_data['company'].unique()]
            location_options = [{'label': location[:40], 'value': location} for location in intermediate_data['location'].unique()]
            type_options = [{'label': type_[:40], 'value': type_} for type_ in intermediate_data['type'].dropna().unique() if isinstance(type_, str)]
            return company_options, location_options, type_options

        @app.callback(
            [Output('menu-tabs-content', 'children'),
             Output('refresh-status', 'children')],
            [Input('menu-tabs', 'value'), Input('refresh-button', 'n_clicks'),
             Input('company-filter', 'value'), Input('location-filter', 'value'), Input('type-filter', 'value')]
        )
        def render_menu_content(selected_menu, n_clicks, companies, locations, types):
            try:
                intermediate_data = reporting.raw_data_reporting.intermediate_load_data(intermediate_data_dir, top_n=None)
                raw_data = reporting.raw_data_reporting.raw_load_data(raw_data_dir)

                if companies:
                    intermediate_data = intermediate_data[intermediate_data['company'].isin(companies)]
                    raw_data = raw_data[raw_data['company'].isin(companies)]
                if locations:
                    intermediate_data = intermediate_data[intermediate_data['location'].isin(locations)]
                    raw_data = raw_data[raw_data['location'].isin(locations)]
                if types:
                    intermediate_data = intermediate_data[intermediate_data['type'].isin(types)]
                    raw_data = raw_data[raw_data['type'].isin(types)]

                refresh_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                refresh_status = f"Last refresh: {refresh_time} - Success"

                if selected_menu == 'menu-1':
                    return [html.Div([
                        html.Div([
                            html.H2("Tabs", style={'textAlign': 'left', 'marginBottom': '10px'}),
                            html.Div([
                                dcc.Tabs(
                                    id='vertical-tabs',
                                    value='tab-1',
                                    children=[
                                        dcc.Tab(label='Tab 1: Job Listings', value='tab-1', style={'padding': '10px'}),
                                        dcc.Tab(label='Tab 2: Raw Processed Data', value='tab-2', style={'padding': '10px'})
                                    ],
                                    vertical=True,
                                    style={'height': '100%', 'borderRight': '1px solid #ccc'}
                                ),
                                html.Div(id='vertical-tabs-content', style={'width': '80%', 'display': 'inline-block', 'padding': '20px'})
                            ], style={'display': 'flex', 'alignItems': 'flex-start'})
                        ])
                    ]), refresh_status]

                elif selected_menu == 'menu-2':
                    return [html.Div([
                        html.Div([
                            html.H2("Tabs", style={'textAlign': 'left', 'marginBottom': '10px'}),
                            html.Div([
                                dcc.Tabs(
                                    id='vertical-tabs-menu-2',
                                    value='tab-1-menu-2',
                                    children=[
                                        dcc.Tab(label='Tab 1: Group by Company and Location Count (Last 3 Months)', value='tab-1-menu-2', style={'padding': '10px'}),
                                        dcc.Tab(label='Tab 2: Group by All Data', value='tab-2-menu-2', style={'padding': '10px'})
                                    ],
                                    vertical=True,
                                    style={'height': '100%', 'borderRight': '1px solid #ccc'}
                                ),
                                html.Div(id='vertical-tabs-content-menu-2', style={'width': '80%', 'display': 'inline-block', 'padding': '20px'})
                            ], style={'display': 'flex', 'alignItems': 'flex-start'})
                        ])
                    ]), refresh_status]

                elif selected_menu == 'menu-3':
                    return [html.Div([
                        html.Div([
                            html.H2("Tabs", style={'textAlign': 'left', 'marginBottom': '10px'}),
                            html.Div([
                                dcc.Tabs(
                                    id='vertical-tabs-menu-3',
                                    value='tab-1-menu-3',
                                    children=[
                                        dcc.Tab(label='Tab 1: Most Recent (1 Day)', value='tab-1-menu-3', style={'padding': '10px'}),
                                        dcc.Tab(label='Tab 2: Last 3 Days', value='tab-2-menu-3', style={'padding': '10px'})
                                    ],
                                    vertical=True,
                                    style={'height': '100%', 'borderRight': '1px solid #ccc'}
                                ),
                                html.Div(id='vertical-tabs-content-menu-3', style={'width': '80%', 'display': 'inline-block', 'padding': '20px'})
                            ], style={'display': 'flex', 'alignItems': 'flex-start'})
                        ])
                    ]), refresh_status]

            except Exception as e:
                refresh_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                refresh_status = f"Last refresh: {refresh_time} - Failed ({str(e)})"
                return [html.Div("Error loading data"), refresh_status]

        @app.callback(
            Output('vertical-tabs-content', 'children'),
            [Input('vertical-tabs', 'value'),
             Input('company-filter', 'value'), Input('location-filter', 'value'), Input('type-filter', 'value')]
        )
        def render_vertical_tab_content(selected_tab, companies, locations, types):
            intermediate_data = reporting.raw_data_reporting.intermediate_load_data(intermediate_data_dir, top_n=None)
            raw_data = reporting.raw_data_reporting.raw_load_data(raw_data_dir)

            if companies:
                intermediate_data = intermediate_data[intermediate_data['company'].isin(companies)]
                raw_data = raw_data[raw_data['company'].isin(companies)]
            if locations:
                intermediate_data = intermediate_data[intermediate_data['location'].isin(locations)]
                raw_data = raw_data[raw_data['location'].isin(locations)]
            if types:
                intermediate_data = intermediate_data[intermediate_data['type'].isin(types)]
                raw_data = raw_data[raw_data['type'].isin(types)]

            if selected_tab == 'tab-1':
                return html.Div([
                    html.H3("Job Listings", style={'textAlign': 'left', 'marginBottom': '10px'}),
                    dash_table.DataTable(
                        id='table-pre-processed',
                        columns=[
                            {"name": i, "id": i, "type": "text", "presentation": "markdown"} if i == 'link' else {"name": i, "id": i}
                            for i in intermediate_data.columns
                        ],
                        data=[
                            {**row, 'link': f"[Click Here]({row['link']})" if 'link' in row else row.get('link', '')}
                            for row in intermediate_data.to_dict('records')
                        ],
                        page_size=10,
                        style_table={'overflowX': 'auto', 'maxWidth': '100%', 'margin': '0 auto'},
                        style_cell={
                            'whiteSpace': 'normal',
                            'textAlign': 'left',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'maxWidth': '150px',
                        },
                        style_header={
                            'backgroundColor': '#f1f1f1',
                            'fontWeight': 'bold',
                            'textAlign': 'center',
                        },
                        sort_action="native",
                        filter_action="native",
                    )
                ])
            elif selected_tab == 'tab-2':
                return html.Div([
                    html.H3("Raw Processed Data", style={'textAlign': 'left', 'marginBottom': '10px'}),
                    dash_table.DataTable(
                        id='table-raw-processed',
                        columns=[
                            {"name": i, "id": i, "type": "text", "presentation": "markdown"} if i == 'link' else {"name": i, "id": i}
                            for i in raw_data.columns
                        ],
                        data=[
                            {**row, 'link': f"[Click Here]({row['link']})" if 'link' in row else row.get('link', '')}
                            for row in raw_data.to_dict('records')
                        ],
                        page_size=10,
                        style_table={'overflowX': 'auto', 'maxWidth': '100%', 'margin': '0 auto'},
                        style_cell={
                            'whiteSpace': 'normal',
                            'textAlign': 'left',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'maxWidth': '150px',
                        },
                        style_header={
                            'backgroundColor': '#f1f1f1',
                            'fontWeight': 'bold',
                            'textAlign': 'center',
                        },
                        sort_action="native",
                        filter_action="native",
                    )
                ])

        @app.callback(
            Output('vertical-tabs-content-menu-2', 'children'),
            [Input('vertical-tabs-menu-2', 'value'),
             Input('company-filter', 'value'), Input('location-filter', 'value'), Input('type-filter', 'value')]
        )
        def render_vertical_tab_content_menu_2(selected_tab, companies, locations, types):
            intermediate_data = reporting.raw_data_reporting.intermediate_load_data(intermediate_data_dir, top_n=None)
            raw_data = reporting.raw_data_reporting.raw_load_data(raw_data_dir)

            if companies:
                intermediate_data = intermediate_data[intermediate_data['company'].isin(companies)]
                raw_data = raw_data[raw_data['company'].isin(companies)]
            if locations:
                intermediate_data = intermediate_data[intermediate_data['location'].isin(locations)]
                raw_data = raw_data[raw_data['location'].isin(locations)]
            if types:
                intermediate_data = intermediate_data[intermediate_data['type'].isin(types)]
                raw_data = raw_data[raw_data['type'].isin(types)]

            if selected_tab == 'tab-1-menu-2':
                if 'posting_date' in intermediate_data.columns:
                    intermediate_data['posting_date'] = pd.to_datetime(intermediate_data['posting_date'])
                    three_months_ago = datetime.now() - pd.DateOffset(months=3)
                    recent_data = intermediate_data[intermediate_data['posting_date'] >= three_months_ago]
                    grouped_data = recent_data.groupby(['company', 'location']).size().reset_index(name='count')
                    return html.Div([
                        html.H3("Grouped Data by Company and Location Count (Last 3 Months)", style={'textAlign': 'left', 'marginBottom': '10px'}),
                        dash_table.DataTable(
                            id='table-grouped-data',
                            columns=[{"name": i, "id": i} for i in grouped_data.columns],
                            data=grouped_data.to_dict('records'),
                            page_size=10,
                            style_table={'overflowX': 'auto', 'maxWidth': '100%', 'margin': '0 auto'},
                            style_cell={
                                'whiteSpace': 'normal',
                                'textAlign': 'left',
                                'overflow': 'hidden',
                                'textOverflow': 'ellipsis',
                                'maxWidth': '150px',
                            },
                            style_header={
                                'backgroundColor': '#f1f1f1',
                                'fontWeight': 'bold',
                                'textAlign': 'center',
                            },
                            sort_action="native",
                            filter_action="native",
                        )
                    ])
                else:
                    return html.Div("Error: 'posting_date' column not found in the dataset")

            elif selected_tab == 'tab-2-menu-2':
                grouped_data = intermediate_data.groupby(['company', 'location']).size().reset_index(name='count')
                return html.Div([
                    html.H3("Grouped Data by All Data", style={'textAlign': 'left', 'marginBottom': '10px'}),
                    dash_table.DataTable(
                        id='table-grouped-data-all',
                        columns=[{"name": i, "id": i} for i in grouped_data.columns],
                        data=grouped_data.to_dict('records'),
                        page_size=10,
                        style_table={'overflowX': 'auto', 'maxWidth': '100%', 'margin': '0 auto'},
                        style_cell={
                            'whiteSpace': 'normal',
                            'textAlign': 'left',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'maxWidth': '150px',
                        },
                        style_header={
                            'backgroundColor': '#f1f1f1',
                            'fontWeight': 'bold',
                            'textAlign': 'center',
                        },
                        sort_action="native",
                        filter_action="native",
                    )
                ])

        @app.callback(
            Output('vertical-tabs-content-menu-3', 'children'),
            [Input('vertical-tabs-menu-3', 'value'),
             Input('company-filter', 'value'), Input('location-filter', 'value'), Input('type-filter', 'value')]
        )
        def render_vertical_tab_content_menu_3(selected_tab, companies, locations, types):
            intermediate_data = reporting.raw_data_reporting.intermediate_load_data(intermediate_data_dir, top_n=None)
            raw_data = reporting.raw_data_reporting.raw_load_data(raw_data_dir)

            if companies:
                intermediate_data = intermediate_data[intermediate_data['company'].isin(companies)]
                raw_data = raw_data[raw_data['company'].isin(companies)]
            if locations:
                intermediate_data = intermediate_data[intermediate_data['location'].isin(locations)]
                raw_data = raw_data[raw_data['location'].isin(locations)]
            if types:
                intermediate_data = intermediate_data[intermediate_data['type'].isin(types)]
                raw_data = raw_data[raw_data['type'].isin(types)]

            if 'posting_date' in intermediate_data.columns:
                intermediate_data['posting_date'] = pd.to_datetime(intermediate_data['posting_date'], errors='coerce').dt.date
                if selected_tab == 'tab-1-menu-3':
                    one_day_ago = datetime.now().date() - timedelta(days=1)
                    recent_data = intermediate_data[intermediate_data['posting_date'] >= one_day_ago]
                    return html.Div([
                        html.H3("Most Recent Jobs (1 Day)", style={'textAlign': 'left', 'marginBottom': '10px'}),
                        dash_table.DataTable(
                            id='table-most-recent-1-day',
                            columns=[
                                {"name": i, "id": i, "type": "text", "presentation": "markdown"} if i == 'link' else {"name": i, "id": i}
                                for i in recent_data.columns
                            ],
                            data=[
                                {**row, 'link': f"[Click Here]({row['link']})" if 'link' in row else row.get('link', '')}
                                for row in recent_data.to_dict('records')
                            ],
                            page_size=10,
                            style_table={'overflowX': 'auto', 'maxWidth': '100%', 'margin': '0 auto'},
                            style_cell={
                                'whiteSpace': 'normal',
                                'textAlign': 'left',
                                'overflow': 'hidden',
                                'textOverflow': 'ellipsis',
                                'maxWidth': '150px',
                            },
                            style_header={
                                'backgroundColor': '#f1f1f1',
                                'fontWeight': 'bold',
                                'textAlign': 'center',
                            },
                            sort_action="native",
                            filter_action="native",
                        )
                    ])
                elif selected_tab == 'tab-2-menu-3':
                    three_days_ago = datetime.now().date() - timedelta(days=3)
                    recent_data = intermediate_data[intermediate_data['posting_date'] >= three_days_ago]
                    return html.Div([
                        html.H3("Jobs Posted in Last 3 Days", style={'textAlign': 'left', 'marginBottom': '10px'}),
                        dash_table.DataTable(
                            id='table-last-3-days',
                            columns=[
                                {"name": i, "id": i, "type": "text", "presentation": "markdown"} if i == 'link' else {"name": i, "id": i}
                                for i in recent_data.columns
                            ],
                            data=[
                                {**row, 'link': f"[Click Here]({row['link']})" if 'link' in row else row.get('link', '')}
                                for row in recent_data.to_dict('records')
                            ],
                            page_size=10,
                            style_table={'overflowX': 'auto', 'maxWidth': '100%', 'margin': '0 auto'},
                            style_cell={
                                'whiteSpace': 'normal',
                                'textAlign': 'left',
                                'overflow': 'hidden',
                                'textOverflow': 'ellipsis',
                                'maxWidth': '150px',
                            },
                            style_header={
                                'backgroundColor': '#f1f1f1',
                                'fontWeight': 'bold',
                                'textAlign': 'center',
                            },
                            sort_action="native",
                            filter_action="native",
                        )
                    ])
            else:
                return html.Div("Error: 'posting_date' column not found in the dataset")

        return app

def main():
    try:
        app = Dashboard.create_app()
        app.run_server(debug=True)
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()

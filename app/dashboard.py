import os
import logging
import pandas as pd
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
from datetime import datetime
import reporting.raw_data_reporting   

# Set up logging
logging.basicConfig(level=logging.INFO)

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
working_dir = os.path.abspath(os.path.join(script_dir, '..'))
os.chdir(working_dir)
logging.info(f"Working directory set to: {working_dir}")

# Global file paths
data_dir = os.path.join(working_dir, 'data', 'pre_processed')
raw_processed_dir = os.path.join(working_dir, 'data', 'raw_processed')

class RawData:
    @staticmethod
    def load_raw_data(data_dir):
        """Load raw data from the directory."""
        files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        return files


class Dashboard:
    @staticmethod
    def create_app():
        """Create a Dash app with horizontal menus and a refresh button."""
        app = dash.Dash(__name__, suppress_callback_exceptions=True)

        app.layout = html.Div([
            html.H1("Job Scrap Dashboard", style={'textAlign': 'center', 'marginBottom': '20px'}),
            html.H2("Developed by Malik Hassan Qayyum", style={'textAlign': 'center', 'marginBottom': '30px', 'color': '#555'}),

            # Refresh Button
            html.Div([
                html.Button("Refresh Data", id="refresh-button", n_clicks=0, style={'marginRight': '10px'}),
                html.Span(id="refresh-status", style={'fontSize': '14px', 'color': '#555'}),
            ], style={'marginBottom': '20px'}),

            # Horizontal Menu
            dcc.Tabs(id='menu-tabs', value='menu-1', children=[
                dcc.Tab(label='Menu 1: Pure CSV', value='menu-1'),
                dcc.Tab(label='Menu 2: Placeholder', value='menu-2'),
                dcc.Tab(label='Menu 3: Placeholder', value='menu-3')
            ]),

            # Content for each menu
            html.Div(id='menu-tabs-content', style={'marginTop': '20px'})
        ])

        @app.callback(
            [Output('menu-tabs-content', 'children'),
             Output('refresh-status', 'children')],
            [Input('menu-tabs', 'value'), Input('refresh-button', 'n_clicks')]
        )
        def render_menu_content(selected_menu, n_clicks):
            try:
                pre_processed_data = reporting.raw_data_reporting.pre_processed_load_data(data_dir)
                raw_processed_data = reporting.raw_data_reporting.raw_processed_load_data(raw_processed_dir)

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
                        html.H2("Menu 2 Content", style={'textAlign': 'center'}),
                        html.P("This menu is reserved for future content.", style={'textAlign': 'center', 'color': '#777'})
                    ]), refresh_status]

                elif selected_menu == 'menu-3':
                    return [html.Div([
                        html.H2("Menu 3 Content", style={'textAlign': 'center'}),
                        html.P("This menu is reserved for future content.", style={'textAlign': 'center', 'color': '#777'})
                    ]), refresh_status]

            except Exception as e:
                refresh_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                refresh_status = f"Last refresh: {refresh_time} - Failed ({str(e)})"
                return [html.Div("Error loading data"), refresh_status]

        @app.callback(
            Output('vertical-tabs-content', 'children'),
            Input('vertical-tabs', 'value')
        )
        def render_vertical_tab_content(selected_tab):
            pre_processed_data = reporting.raw_data_reporting.pre_processed_load_data(data_dir)
            raw_processed_data = reporting.raw_data_reporting.raw_processed_load_data(raw_processed_dir)

            if selected_tab == 'tab-1':
                return html.Div([
                    html.H3("Job Listings", style={'textAlign': 'left', 'marginBottom': '10px'}),
                    dash_table.DataTable(
                        id='table-pre-processed',
                        columns=[
                            {"name": i, "id": i, "type": "text", "presentation": "markdown"} if i == 'link' else {"name": i, "id": i}
                            for i in pre_processed_data.columns
                        ],
                        data=[
                            {**row, 'link': f"[Click Here]({row['link']})" if 'link' in row else row.get('link', '')}
                            for row in pre_processed_data.to_dict('records')
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
                            for i in raw_processed_data.columns
                        ],
                        data=[
                            {**row, 'link': f"[Click Here]({row['link']})" if 'link' in row else row.get('link', '')}
                            for row in raw_processed_data.to_dict('records')
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

        return app

def main():
    try:
        app = Dashboard.create_app()
        app.run_server(debug=True)
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()

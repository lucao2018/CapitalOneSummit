import dash_core_components as dcc
import dash_html_components as html
import datetime
# import pandas as pd
# import plotly.graph_objs as go
# from dash.dependencies import Input, Output, State
# from dash.exceptions import PreventUpdate
# import dash_bootstrap_components as dbc
# import dash_table
import dash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Tabs(id="tabs", children=[

        dcc.Tab(label='Search for Jeopardy Questions', children=[

            html.Br(),

            html.H2(children="Welcome to Jeopardy Trivia Lookup", style={
                'textAlign': 'center',
            }),

            html.Br(),
            html.Br(),
            html.Div([
                html.H5(children="Fill in criteria that is relevant to your search and then click submit: "),
                html.Div([
                    html.H6(children="Type in the value of the clue in dollars (difficulty): "),
                    dcc.Input(
                        id='clue-value',
                        type='text',
                        value = 'Clue value in $'
                    ),
                    html.H6(children="Type in the category of the clue that you want to search for: "),
                    dcc.Input(
                        id = 'category-value',
                        type = 'text',
                        value = 'Clue category'
                    ),
                    html.H6(children="Type in the range of dates that you would like to see clues from: "),
                    dcc.Input(
                        id = 'min-date',
                        type = 'text',
                        value = 'mm/dd/yyyy'
                    ),
                    dcc.Input(
                        id = 'max-date',
                        type = 'text',
                        value = 'mm/dd/yyyy'
                    )

                ]),

            ]),
            html.Button(id='submit-button', n_clicks=0, children='Submit'),
        ]),

    ])
])
if __name__ == '__main__':
    app.run_server(debug=True)

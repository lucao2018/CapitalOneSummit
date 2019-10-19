import dash_core_components as dcc
import dash_html_components as html
import dash_table
import datetime
import requests
import datetime
import pandas as pd
# import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
# import dash_bootstrap_components as dbc
import dash_table
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
                    html.H6(children="Type in the value of the clue in dollars (omit the dollar sign): "),
                    dcc.Input(
                        id='clue-value',
                        type='text',
                    ),
                    html.H6(children="Type in the category of the clue that you want to search for: "),
                    dcc.Input(
                        id='category-value',
                        type='text',
                    ),
                    html.H6(children="Type in the range of dates that you would like to see clues from (mm/dd/yyyy): "),
                    dcc.Input(
                        id='min-date',
                        type='text',
                    ),
                    dcc.Input(
                        id='max-date',
                        type='text',
                    )
                ]),

            ]),
            html.Button(id='submit-button', n_clicks=0, children='Submit'),
            html.Div(
                dash_table.DataTable(
                    id='datatable',
                    style_table={'overflowX': 'scroll'},
                    style_cell={
                        'whiteSpace': 'normal'
                    },

                    columns=[{"name": "Question Value", "id": "value"},
                             {"name": "Question", "id": "question"},
                             {"name": "Answer", "id": "answer"},
                             {"name": "Category", "id": "Category Names"},
                             {"name": "Category ID", "id": "category_id"},
                             {"name": "Air Date", "id": "airdate"}],
                    data=[],
                    css=[{
                        'selector': '.dash-cell div.dash-cell-value',
                        'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
                    }],
                    editable=True,
                    sort_action="custom",
                    sort_mode="multi",
                    sort_by=[],
                    row_selectable="multi",
                    row_deletable=True,
                    selected_rows=[],
                    page_action="custom",
                    page_current=0,
                    page_size=15,
                ),
            ),
            html.Div(id='intermediate-value', style={'display': 'none'}),
            html.Button(id='submit-button2', n_clicks=0, children='Add selected questions to favorites'),
        ]),

        dcc.Tab(label="Your saved questions", children=[
            html.Div(
                dash_table.DataTable(
                    id='datatable2',
                    style_table={'overflowX': 'scroll'},
                    style_cell={
                        'whiteSpace': 'normal'
                    },

                    columns=[{"name": "Question Value", "id": "value"},
                             {"name": "Question", "id": "question"},
                             {"name": "Answer", "id": "answer"},
                             {"name": "Category", "id": "Category Names"},
                             {"name": "Category ID", "id": "category_id"},
                             {"name": "Air Date", "id": "airdate"}],
                    data=[],
                    css=[{
                        'selector': '.dash-cell div.dash-cell-value',
                        'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
                    }],
                    editable=True,
                    sort_action="custom",
                    sort_mode="multi",
                    sort_by=[],
                    row_selectable="multi",
                    row_deletable=True,
                    selected_rows=[],
                    page_action="custom",
                    page_current=0,
                    page_size=15,
                ),
            ),
        ])

    ])
])


def parse_date(date_string):
    if (date_string == None):
        return None

    format_str = '%m/%d/%Y'  # The format
    datetime_obj = datetime.datetime.strptime(date_string, format_str)
    return datetime_obj


def make_api_call(clue_value, category_value, min_date, max_date):
    parameters = {
        "value": clue_value,
        "category_value": category_value,
        "min_date": parse_date(min_date),
        "max_date": parse_date(max_date)
    }
    response = requests.get("http://jservice.io/api/clues/", params=parameters)
    return response.json()


@app.callback(Output('datatable', 'data'),
              [Input('submit-button', 'n_clicks')],
              [State('clue-value', 'value'),
               State('category-value', 'value'),
               State('min-date', 'value'),
               State('max-date', 'value')])
def generate_table(n_clicks, input1, input2, input3, input4):
    if input1 != None or input2 != None or input3 != None or input4 != None:
        jsonResponse = make_api_call(input1, input2, input3, input4)
        data = pd.DataFrame.from_dict(jsonResponse)
        categoryNames = []
        for item in data['category']:
            categoryNames.append(item['title'])
        data['Category Names'] = categoryNames
        return data.to_dict(orient='records')
    else:
        raise PreventUpdate

@app.callback(Output('datatable2', 'data'),
              [Input('submit-button2', 'n_clicks')],
              [State('datatable', 'selected_rows'),
               State('datatable2', 'data'),
               State('datatable', 'data')])
def printData(n_clicks, input1, input2, input3):
    favorites_list = input2
    for selected_row in input1:
        if input3[selected_row] not in favorites_list:
            favorites_list.append(input3[selected_row])
    return favorites_list

if __name__ == '__main__':
    app.run_server(debug=True)

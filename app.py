import dash_core_components as dcc
import dash_html_components as html
import requests
import datetime
import pandas as pd
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_table
import dash
from JeopardyGame import JeopardyGame

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True

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
                    html.H6(children="Type in the category id of the clue that you want to search for: "),
                    html.Br(),
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

        dcc.Tab(label="Your Favorite Questions", children=[
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
        ]),
        dcc.Tab(label="Play Jeopardy!", children=[
            dbc.Button("Click To Start A New Game", color="primary", id='play-button'),
            html.Div(id='table-div', children=[

            ]),
            html.Div(id="score", children=200),
            html.Div(id='answers', style={'display': 'none'})
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


@app.callback([Output('datatable', 'data'), Output('datatable', 'selected_rows')],
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
        return data.to_dict(orient='records'), []
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


@app.callback([
    Output('table-div', 'children'),
    Output('answers', 'children')
], [Input('play-button', 'n_clicks')])
def startJeopardy(n_clicks):
    if n_clicks == None:
        raise PreventUpdate
    else:
        game = JeopardyGame()
        game.generate_categories()
        game.generate_category_titles()
        game.generate_questions()

        questions = game.get_questions()
        answers = game.get_answers()
        categories = game.get_categories()
        print(answers)

        headers = []
        for category in categories:
            headers.append(html.Td(category))

        table_header = [
            html.Thead(html.Tr(headers), style={
                'color': '#FFCC00',
                'font-weight': 'bold',
                'font-size': '30px',
                'text-align': 'center',
            })
        ]

        row_list = []
        clue_value = 0
        for i in range(0, 25):
            if i % 5 == 0:
                clue_value += 200
            row_list.append(
                html.Td(html.Div([
                    html.A(
                        [html.Span(html.U('$' + str(clue_value)), id=("popover-target" + str(i)), style={
                            'textAlign': 'center',
                            'color': '#FFCC00',
                            'font-weight': 'bold',
                            'font-size': '16px'
                        })]
                    ),
                    dbc.Popover(
                        [
                            dbc.PopoverHeader(questions[i]),
                            dbc.Input(
                                id='input' + str(i)
                            ),

                            dbc.Button(id='check-question-button' + str(i), style={
                                "color": "blue"
                            }, children=html.Span("Submit Your Answer", style={
                                "color": "#FFCC00"
                            }))
                        ],
                        id=("popover" + str(i)),
                        is_open=False,
                        target=("popover-target" + str(i)),
                    ),
                ]
                )))

        row1 = html.Tr(row_list[0:5], style={
            'text-align': 'center'
        })
        row2 = html.Tr(row_list[5:10], style={
            'text-align': 'center'
        })
        row3 = html.Tr(row_list[10:15], style={
            'text-align': 'center'
        })
        row4 = html.Tr(row_list[15:20], style={
            'text-align': 'center'
        })
        row5 = html.Tr(row_list[20:25], style={
            'text-align': 'center'
        })

        table_body = [html.Tbody([row1, row2, row3, row4, row5])]

        table = dbc.Table(table_header + table_body, bordered=True, style={
            'background-color': '#060CE9'
        })
        return table, answers


@app.callback(
    Output("score", "children"),
    [Input("check-question-button0", "n_clicks")],
    [State('score', 'children'),
     State('input0', 'value'),
     State('answers', 'children')],
)
def checkQuestion1(n, currentScore, candidateAnswer, actualAnswers):
    if candidateAnswer == None:
        raise PreventUpdate
    else:
        if candidateAnswer == actualAnswers[0]:
            currentScore += 200
        else:
            currentScore -= 200
    return currentScore


@app.callback(
    Output("popover0", "is_open"),
    [Input("popover-target0", "n_clicks")],
    [State("popover0", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover1", "is_open"),
    [Input("popover-target1", "n_clicks")],
    [State("popover1", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover2", "is_open"),
    [Input("popover-target2", "n_clicks")],
    [State("popover2", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover3", "is_open"),
    [Input("popover-target3", "n_clicks")],
    [State("popover3", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover4", "is_open"),
    [Input("popover-target4", "n_clicks")],
    [State("popover4", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover5", "is_open"),
    [Input("popover-target5", "n_clicks")],
    [State("popover5", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover6", "is_open"),
    [Input("popover-target6", "n_clicks")],
    [State("popover6", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover7", "is_open"),
    [Input("popover-target7", "n_clicks")],
    [State("popover7", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover8", "is_open"),
    [Input("popover-target8", "n_clicks")],
    [State("popover8", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover9", "is_open"),
    [Input("popover-target9", "n_clicks")],
    [State("popover9", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover10", "is_open"),
    [Input("popover-target10", "n_clicks")],
    [State("popover10", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover11", "is_open"),
    [Input("popover-target11", "n_clicks")],
    [State("popover11", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover12", "is_open"),
    [Input("popover-target12", "n_clicks")],
    [State("popover12", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover13", "is_open"),
    [Input("popover-target13", "n_clicks")],
    [State("popover13", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover14", "is_open"),
    [Input("popover-target14", "n_clicks")],
    [State("popover14", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover15", "is_open"),
    [Input("popover-target15", "n_clicks")],
    [State("popover15", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover16", "is_open"),
    [Input("popover-target16", "n_clicks")],
    [State("popover16", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover17", "is_open"),
    [Input("popover-target17", "n_clicks")],
    [State("popover17", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover18", "is_open"),
    [Input("popover-target18", "n_clicks")],
    [State("popover18", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover19", "is_open"),
    [Input("popover-target19", "n_clicks")],
    [State("popover19", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover20", "is_open"),
    [Input("popover-target20", "n_clicks")],
    [State("popover20", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover21", "is_open"),
    [Input("popover-target21", "n_clicks")],
    [State("popover21", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover22", "is_open"),
    [Input("popover-target22", "n_clicks")],
    [State("popover22", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover23", "is_open"),
    [Input("popover-target23", "n_clicks")],
    [State("popover23", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover24", "is_open"),
    [Input("popover-target24", "n_clicks")],
    [State("popover24", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == '__main__':
    app.run_server(debug=True)

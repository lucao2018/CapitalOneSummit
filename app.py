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
from flask_sqlalchemy import SQLAlchemy

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.config.suppress_callback_exceptions = True
server.config[
    'SQLALCHEMY_DATABASE_URI'] = 'postgres://flaehrpkwiurco:ad15ed7406fa968214c230eca578ba83793420015f135cb9b34409da1b3e51c6@ec2-54-235-180-123.compute-1.amazonaws.com:5432/d5ovqc3h4eto64'
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(server)


class JeopardyTable(db.Model):
    __tablename__ = 'jeopardy'
    category = db.Column(db.String)
    category_id = db.Column(db.Integer, primary_key=True)

    def __init__(self, category, category_id):
        self.category = category
        self.category_id = category_id


def make_category_call(offset):
    parameters = {
        "count": 100,
        "offset": offset
    }
    response = requests.get("http://jservice.io/api/categories/", params=parameters)
    return response.json()


def populateDatabase():
    offset = 0
    while True:
        response = make_category_call(offset)
        if (len(response) == 0):
            break
        for item in response:
            category_id = item['id']
            category_title = item['title']
            if (category_id is not None and category_title is not None):
                if db.session.query(JeopardyTable).filter(JeopardyTable.category_id == category_id).count() == 0:
                    data = JeopardyTable(category_title, category_id)
                    db.session.add(data)
                    db.session.commit()
        offset += 100


# populateDatabase()

app.layout = html.Div([

    dcc.Tabs(id="tabs", children=[
        dcc.Tab(label='Search for Jeopardy Questions', children=[

            html.Div([

                html.Br(),

                html.H2(children="Jeopardy Trivia Search Engine", style={
                    'textAlign': 'center',
                }),

                html.Br(),

                html.Div(id='search', style={
                    'display': 'flex',
                    'justify-content': 'center',
                    # 'margin-top': '0',
                    # 'margin-bottom': '0',
                    # 'margin-right': 'auto',
                    # 'margin-left': 'auto'
                }, children=[
                    html.Div([
                        html.Div(style={
                            'display': 'flex',
                            'justify-content': 'center'
                        }, children=[
                            html.H6(children="Search for a category by key word/phrase (required)", style={
                                'margin-left': '1em'
                            })
                        ]),
                        html.Div(style={
                            'display': 'flex',
                            'justify-content': 'center'
                        },
                            children=[
                                dbc.Input(
                                    id='category-value',
                                    type='text',
                                    style={
                                        'margin-left': '1em',
                                        'width': '300px',
                                    },
                                    placeholder="Potpourri",
                                ),
                            ]),

                        html.Br(),
                        html.Div(style={
                            'display': 'flex',
                            'justify-content': 'center'
                        },
                            children=[html.H6(
                                children="Type in the value of the clue in dollars (omit the dollar sign): ",
                                style={
                                    'margin-left': '1em'

                                },
                            ),
                            ]),

                        html.Div(style={
                            'display': 'flex',
                            'justify-content': 'center'
                        }, children=[
                            dbc.Input(
                                id='clue-value',
                                style={
                                    'margin-left': '1em',
                                    'width': '300px'
                                },
                                placeholder=200,
                                type="number"
                            ),
                        ]),

                        html.Br(),
                        html.Div(style={
                            'display': 'flex',
                            'justify-content': 'center'
                        }, children=[
                            html.H6(
                                children="Type in the range of dates that you would like to see clues from: ",
                                style={
                                    'margin-left': '1em'
                                }
                            )
                        ]),

                        dbc.Row([
                            dbc.Input(
                                id='min-date',
                                type='text',
                                style={
                                    'margin-left': '2em',
                                    'width': '300px'
                                },
                                placeholder='mm/dd/yyyy',
                            ),
                            dbc.Input(
                                id='max-date',
                                type='text',
                                style={
                                    'margin-left': '1em',
                                    'width': '300px'
                                },
                                placeholder='mm/dd/yyyy',
                            )]),
                        html.Br(),
                        html.Div(style={
                            'display': 'flex',
                            'justify-content': 'center'
                        },
                            children=[html.H6(children="How many clues would you like be returned",
                                              style={
                                                  'margin-left': '1em'
                                              }
                                              ), ]
                        ),

                        html.Div(style={
                            'display': 'flex',
                            'justify-content': 'center'
                        }, children=[
                            dbc.Input(
                                id='num-clues',
                                type='number',
                                style={
                                    'margin-left': '1em',
                                    'width': '300px'
                                },
                                placeholder=100

                            ),
                        ]),

                    ]),

                ]),
                html.Br(),
                html.Div(style={
                    'display': 'flex',
                    'justify-content': 'center'
                }, children=[
                    dbc.Button(id='submit-button', n_clicks=0, children='Search',
                               style={
                                   'margin-left': '1em'
                               }
                               )
                ]),

            ]),

            html.Br(),

            html.Div(id='datatable-div', children=[
            ]),
            html.Br(),
            html.Div(id='favorites-button-div', children=[
            ]),

            html.Div(id='intermediate-value', style={'display': 'none'}),
        ]),

        dcc.Tab(label="Your Favorite Questions", children=[
            html.Div(
                dash_table.DataTable(
                    id='datatable2',
                    style_table={
                        'width': '97.5%',
                        'margin-left': 'auto',
                        'margin-right': 'auto',
                        'padding-top': '15px'
                    },
                    style_header={
                        'backgroundColor': 'white',
                        'fontWeight': 'bold'
                    },
                    page_size=20,
                    style_cell={
                        'whiteSpace': 'normal',
                        'minWidth': '0px', 'maxWidth': '280px',
                    },
                    style_cell_conditional=[
                        {'if': {'column_id': 'value'},
                         'width': '20px'},
                        {'if': {'column_id': 'category_id'},
                         'width': '30px'},
                        {'if': {'column_id': 'Category Names'},
                         'textAlign': 'left',
                         'width': '250px'},
                        {'if': {'column_id': 'question'},
                         'textAlign': 'left'},
                        {'if': {'column_id': 'answer'},
                         'textAlign': 'left',
                         'width': '120px'},
                        {'if': {'column_id': 'airdate'},
                         'width': '120px'},
                    ],

                    columns=[{"name": "Value", "id": "value"},
                             {"name": "Question", "id": "question"},
                             {"name": "Answer", "id": "answer"},
                             {"name": "Category", "id": "Category Names"},
                             {"name": "Category ID", "id": "category_id"},
                             {"name": "Air Date", "id": "airdate"}],
                    data=[],
                    row_selectable="multi",
                    row_deletable=True,
                    selected_rows=[],
                    page_action='native',
                    page_current=0,
                ),
            ),
        ]),

        dcc.Tab(label="Play Jeopardy!", children=[
            html.Br(),
            html.Div(id='table-div', children=[

            ]),
            html.Div(id="score", children=[

            ]),
            html.Div(id='play-div', style={
                'display': 'flex',
                'justify-content': 'center',
                'align-items': 'center',
                'padding-top': '50px'
            },
                     children=[
                         dbc.Button("Click To Start A New Game", id='play-button'),
                     ]),

            html.Div(children=[

            ]),
            html.Div(id='answers', style={'display': 'none'}),
            html.Div(id='used-buttons', style={'display': 'none'}, children=[

            ]),
        ])
    ])
])


def parse_date(date_string):
    if (date_string == None):
        return None

    format_str = '%m/%d/%Y'  # The format
    datetime_obj = datetime.datetime.strptime(date_string, format_str)
    return datetime_obj


def make_api_call(clue_value, category_value, min_date, max_date, offset):
    parameters = {
        "value": clue_value,
        "category": category_value,
        "min_date": parse_date(min_date),
        "max_date": parse_date(max_date),
        "offset": offset
    }
    response = requests.get("http://jservice.io/api/clues/", params=parameters)
    return response.json()


@app.callback([Output('datatable-div', 'children'), Output('favorites-button-div', 'children')],
              [Input('submit-button', 'n_clicks')],
              [State('clue-value', 'value'),
               State('category-value', 'value'),
               State('min-date', 'value'),
               State('max-date', 'value'),
               State('num-clues', 'value')])
def generate_table(n_clicks, input1, input2, input3, input4, input5):
    list_of_matching_ids = []
    table_data = []

    if n_clicks != 0:
        if input2 is None or input2 == "":
            return dbc.Alert("A required field was not filled out", color="danger", dismissable=True), []
        else:
            listOfMatches = JeopardyTable.query.filter(JeopardyTable.category.contains(input2)).all()
            for category in listOfMatches:
                list_of_matching_ids.append(category.category_id)
            for id in list_of_matching_ids:
                if input5 is not None:
                    if (len(table_data) >= int(input5)):
                        break
                jsonResponse = make_api_call(input1, id, input3, input4, 0)
                table_data += jsonResponse
            data = pd.DataFrame.from_dict(table_data)

            categoryNames = []

            for item in data['category']:
                categoryNames.append(item['title'])
            data['Category Names'] = categoryNames

            return [dash_table.DataTable(
                id='datatable',

                style_table={
                    'width': '97.5%',
                    'margin-left': 'auto',
                    'margin-right': 'auto'
                },
                style_header={
                    'backgroundColor': 'white',
                    'fontWeight': 'bold'
                },
                page_size=20,
                style_cell={
                    'whiteSpace': 'normal',
                    'minWidth': '0px', 'maxWidth': '280px',
                },
                style_cell_conditional=[
                    {'if': {'column_id': 'value'},
                     'width': '20px'},
                    {'if': {'column_id': 'category_id'},
                     'width': '30px'},
                    {'if': {'column_id': 'Category Names'},
                     'textAlign': 'left',
                     'width': '250px'},
                    {'if': {'column_id': 'question'},
                     'textAlign': 'left'},
                    {'if': {'column_id': 'answer'},
                     'textAlign': 'left',
                     'width': '120px'},
                    {'if': {'column_id': 'airdate'},
                     'width': '120px'},
                ],

                columns=[{"name": "Value", "id": "value"},
                         {"name": "Question", "id": "question"},
                         {"name": "Answer", "id": "answer"},
                         {"name": "Category", "id": "Category Names"},
                         {"name": "Category ID", "id": "category_id"},
                         {"name": "Air Date", "id": "airdate"}],
                data=data.to_dict(orient='records'),
                row_selectable="multi",
                row_deletable=True,
                selected_rows=[],
                page_action='native',
                page_current=0,
            ), dbc.Button(id='submit-button2', n_clicks=0, children='Save To Favorites', style={
                'margin-left': '1em',
                'margin-bottom': '1em'
            })]

    else:
        raise PreventUpdate


@app.callback([
    Output('table-div', 'children'),
    Output('answers', 'children'),
    Output('score', 'children'),
    Output('play-div', 'style')],
    [Input('play-button', 'n_clicks')])
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
                    html.A([
                        dbc.Button(html.U('$' + str(clue_value), style={
                            'color': '#FFCC00',
                            'font-weight': 'bold'
                        }), color="link", id="modal-button" + str(i))
                    ]),
                    dbc.Modal(
                        [
                            dbc.ModalHeader(questions[i]),
                            dbc.ModalBody("What is/are ...."),
                            dbc.ModalFooter([
                                dbc.Input(id='answer' + str(i)),
                                dbc.Button("Submit", id="check-question-button" + str(i), className="ml-auto"+str(i)),
                            ]

                            ),
                        ],
                        id="modal" + str(i), backdrop=True),
                ])))

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
            'background-color': '#060CE9',
            'width': '97.5%',
            'margin-left': 'auto',
            'margin-right': 'auto',
            'padding-top': '15px',
            'bordered': True,
        })

        return table, answers, html.Div(
            children=[dbc.Button(["Score ", dbc.Badge(id="score-button", color="light", children=0)], color="primary")],
            style={
                'display': 'flex',
                'justify-content': 'center'
            }), {'display': 'flex',
                 'justify-content': 'center',
                 'align-items': 'center',
                 'padding-top': '15px'}


@app.callback(
    [Output('modal0', 'style'), Output('modal-button0', 'style'),
     Output('modal1', 'style'), Output('modal-button1', 'style'),
     Output('modal2', 'style'), Output('modal-button2', 'style'),
     Output('modal3', 'style'), Output('modal-button3', 'style'),
     Output('modal4', 'style'), Output('modal-button4', 'style'),
     Output('modal5', 'style'), Output('modal-button5', 'style'),
     Output('modal6', 'style'), Output('modal-button6', 'style'),
     Output('modal7', 'style'), Output('modal-button7', 'style'),
     Output('modal8', 'style'), Output('modal-button8', 'style'),
     Output('modal9', 'style'), Output('modal-button9', 'style'),
     Output('modal10', 'style'), Output('modal-button10', 'style'),
     Output('modal11', 'style'), Output('modal-button11', 'style'),
     Output('modal12', 'style'), Output('modal-button12', 'style'),
     Output('modal13', 'style'), Output('modal-button13', 'style'),
     Output('modal14', 'style'), Output('modal-button14', 'style'),
     Output('modal15', 'style'), Output('modal-button15', 'style'),
     Output('modal16', 'style'), Output('modal-button16', 'style'),
     Output('modal17', 'style'), Output('modal-button17', 'style'),
     Output('modal18', 'style'), Output('modal-button18', 'style'),
     Output('modal19', 'style'), Output('modal-button19', 'style'),
     Output('modal20', 'style'), Output('modal-button20', 'style'),
     Output('modal21', 'style'), Output('modal-button21', 'style'),
     Output('modal22', 'style'), Output('modal-button22', 'style'),
     Output('modal23', 'style'), Output('modal-button23', 'style'),
     Output('modal24', 'style'), Output('modal-button24', 'style'),
     Output('score-button', 'children'), Output('used-buttons', 'children')
     ],
    [Input("check-question-button0", "n_clicks"),
     Input("check-question-button1", "n_clicks"),
     Input("check-question-button2", "n_clicks"),
     Input("check-question-button3", "n_clicks"),
     Input("check-question-button4", "n_clicks"),
     Input("check-question-button5", "n_clicks"),
     Input("check-question-button6", "n_clicks"),
     Input("check-question-button7", "n_clicks"),
     Input("check-question-button8", "n_clicks"),
     Input("check-question-button9", "n_clicks"),
     Input("check-question-button10", "n_clicks"),
     Input("check-question-button11", "n_clicks"),
     Input("check-question-button12", "n_clicks"),
     Input("check-question-button13", "n_clicks"),
     Input("check-question-button14", "n_clicks"),
     Input("check-question-button15", "n_clicks"),
     Input("check-question-button16", "n_clicks"),
     Input("check-question-button17", "n_clicks"),
     Input("check-question-button18", "n_clicks"),
     Input("check-question-button19", "n_clicks"),
     Input("check-question-button20", "n_clicks"),
     Input("check-question-button21", "n_clicks"),
     Input("check-question-button22", "n_clicks"),
     Input("check-question-button23", "n_clicks"),
     Input("check-question-button24", "n_clicks")],
    [State('answer0', 'value'),
     State('answer1', 'value'),
     State('answer2', 'value'),
     State('answer3', 'value'),
     State('answer4', 'value'),
     State('answer5', 'value'),
     State('answer6', 'value'),
     State('answer7', 'value'),
     State('answer8', 'value'),
     State('answer9', 'value'),
     State('answer10', 'value'),
     State('answer11', 'value'),
     State('answer12', 'value'),
     State('answer13', 'value'),
     State('answer14', 'value'),
     State('answer15', 'value'),
     State('answer16', 'value'),
     State('answer17', 'value'),
     State('answer18', 'value'),
     State('answer19', 'value'),
     State('answer20', 'value'),
     State('answer21', 'value'),
     State('answer22', 'value'),
     State('answer23', 'value'),
     State('answer24', 'value'),
     State('score-button', 'children'),
     State('answers', 'children'),
     State('used-buttons', 'children')])
def checkAnswer(n_clicks0, n_clicks1, n_clicks2, n_clicks3, n_clicks4, n_clicks5, n_clicks6, n_clicks7, n_clicks8,
                n_clicks9,
                n_clicks10, n_clicks11, n_clicks12, n_clicks13, n_clicks14, n_clicks15, n_clicks16, n_clicks17,
                n_clicks18, n_clicks19,
                n_clicks20, n_clicks21, n_clicks22, n_clicks23, n_clicks24, answer0, answer1, answer2,
                answer3, answer4, answer5, answer6, answer7, answer8, answer9, answer10, answer11, answer12, answer13
                , answer14, answer15, answer16, answer17, answer18, answer19, answer20, answer21, answer22, answer23,
                answer24, currentScore, answers, usedButtons):
    ctx = dash.callback_context
    buttonNum = ctx.triggered[0]['prop_id'].split('.')[0]
    buttonNum = extract_num(buttonNum)
    if buttonNum == 0:
        currentScore = update_score(answer0, buttonNum, answers, currentScore)
    elif buttonNum == 1:
        currentScore = update_score(answer1, buttonNum, answers, currentScore)
    elif buttonNum == 2:
        currentScore = update_score(answer2, buttonNum, answers, currentScore)
    elif buttonNum == 3:
        currentScore = update_score(answer3, buttonNum, answers, currentScore)
    elif buttonNum == 4:
        currentScore = update_score(answer4, buttonNum, answers, currentScore)
    elif buttonNum == 5:
        currentScore = update_score(answer5, buttonNum, answers, currentScore)
    elif buttonNum == 6:
        currentScore = update_score(answer6, buttonNum, answers, currentScore)
    elif buttonNum == 7:
        currentScore = update_score(answer7, buttonNum, answers, currentScore)
    elif buttonNum == 8:
        currentScore = update_score(answer8, buttonNum, answers, currentScore)
    elif buttonNum == 9:
        currentScore = update_score(answer9, buttonNum, answers, currentScore)
    elif buttonNum == 10:
        currentScore = update_score(answer10, buttonNum, answers, currentScore)
    elif buttonNum == 11:
        currentScore = update_score(answer11, buttonNum, answers, currentScore)
    elif buttonNum == 12:
        currentScore = update_score(answer12, buttonNum, answers, currentScore)
    elif buttonNum == 13:
        currentScore = update_score(answer13, buttonNum, answers, currentScore)
    elif buttonNum == 14:
        currentScore = update_score(answer14, buttonNum, answers, currentScore)
    elif buttonNum == 15:
        currentScore = update_score(answer15, buttonNum, answers, currentScore)
    elif buttonNum == 16:
        currentScore = update_score(answer16, buttonNum, answers, currentScore)
    elif buttonNum == 17:
        currentScore = update_score(answer17, buttonNum, answers, currentScore)
    elif buttonNum == 18:
        currentScore = update_score(answer18, buttonNum, answers, currentScore)
    elif buttonNum == 19:
        currentScore = update_score(answer19, buttonNum, answers, currentScore)
    elif buttonNum == 20:
        currentScore = update_score(answer20, buttonNum, answers, currentScore)
    elif buttonNum == 21:
        currentScore = update_score(answer21, buttonNum, answers, currentScore)
    elif buttonNum == 22:
        currentScore = update_score(answer22, buttonNum, answers, currentScore)
    elif buttonNum == 23:
        currentScore = update_score(answer23, buttonNum, answers, currentScore)
    elif buttonNum == 24:
        currentScore = update_score(answer24, buttonNum, answers, currentScore)
    usedButtons.append(buttonNum)

    outputList = []

    for i in range(0, 25):
        if i not in usedButtons:
            outputList.append({})
            outputList.append({
                'color': '#FFCC00',
                'font-weight': 'bold'
            })
        else:
            outputList.append({'display': 'none'})
            outputList.append({'display': 'none'})

    outputList.append(currentScore)
    outputList.append(usedButtons)

    return outputList


def extract_num(buttonNum):
    output = ""
    for i in range(len(buttonNum)):
        if buttonNum[i].isdigit():
            output += buttonNum[i]
    return int(output)


def update_score(answer, buttonNum, answers, currentScore):
    if answer == answers[buttonNum]:
        if (buttonNum <= 4):
            currentScore += 200
        elif buttonNum <= 9:
            currentScore += 400
        elif buttonNum <= 14:
            currentScore += 600
        elif buttonNum <= 19:
            currentScore += 800
        elif buttonNum <= 24:
            currentScore += 1000
    else:
        if (buttonNum <= 4):
            currentScore -= 200
        elif buttonNum <= 9:
            currentScore -= 400
        elif buttonNum <= 14:
            currentScore -= 600
        elif buttonNum <= 19:
            currentScore -= 800
        elif buttonNum <= 24:
            currentScore -= 1000
    return currentScore


@app.callback(
    Output("modal0", "is_open"),
    [Input("modal-button0", "n_clicks")],
    [State("modal0", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal1", "is_open"),
    [Input("modal-button1", "n_clicks")],
    [State("modal1", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal2", "is_open"),
    [Input("modal-button2", "n_clicks")],
    [State("modal2", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal3", "is_open"),
    [Input("modal-button3", "n_clicks")],
    [State("modal3", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal4", "is_open"),
    [Input("modal-button4", "n_clicks")],
    [State("modal4", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal5", "is_open"),
    [Input("modal-button5", "n_clicks")],
    [State("modal5", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal6", "is_open"),
    [Input("modal-button6", "n_clicks")],
    [State("modal6", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal7", "is_open"),
    [Input("modal-button7", "n_clicks")],
    [State("modal7", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal8", "is_open"),
    [Input("modal-button8", "n_clicks")],
    [State("modal8", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal9", "is_open"),
    [Input("modal-button9", "n_clicks")],
    [State("modal9", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal10", "is_open"),
    [Input("modal-button10", "n_clicks")],
    [State("modal10", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal11", "is_open"),
    [Input("modal-button11", "n_clicks")],
    [State("modal11", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal12", "is_open"),
    [Input("modal-button12", "n_clicks")],
    [State("modal12", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal13", "is_open"),
    [Input("modal-button13", "n_clicks")],
    [State("modal13", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal14", "is_open"),
    [Input("modal-button14", "n_clicks")],
    [State("modal14", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal15", "is_open"),
    [Input("modal-button15", "n_clicks")],
    [State("modal15", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal16", "is_open"),
    [Input("modal-button16", "n_clicks")],
    [State("modal16", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal17", "is_open"),
    [Input("modal-button17", "n_clicks")],
    [State("modal17", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal18", "is_open"),
    [Input("modal-button18", "n_clicks")],
    [State("modal18", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal19", "is_open"),
    [Input("modal-button19", "n_clicks")],
    [State("modal19", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal20", "is_open"),
    [Input("modal-button20", "n_clicks")],
    [State("modal20", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal21", "is_open"),
    [Input("modal-button21", "n_clicks")],
    [State("modal21", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal22", "is_open"),
    [Input("modal-button22", "n_clicks")],
    [State("modal22", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal23", "is_open"),
    [Input("modal-button23", "n_clicks")],
    [State("modal23", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal24", "is_open"),
    [Input("modal-button24", "n_clicks")],
    [State("modal24", "is_open")],
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == '__main__':
    app.run_server(debug=True)

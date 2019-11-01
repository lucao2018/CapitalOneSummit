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
server.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://flaehrpkwiurco:ad15ed7406fa968214c230eca578ba83793420015f135cb9b34409da1b3e51c6@ec2-54-235-180-123.compute-1.amazonaws.com:5432/d5ovqc3h4eto64'
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
                    print("added")
        offset += 100


# populateDatabase()

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
                    html.H6(children="Search for a category by key word/phrase"),
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
                    ),
                    html.H6(children="How many clues would you like be returned (approximate)"),
                    dcc.Input(
                        id='num-clues',
                        type='text',
                    ),
                ]),

            ]),
            html.Button(id='submit-button', n_clicks=0, children='Submit'),

            html.Div(
                dash_table.DataTable(
                    id='datatable',
                    style_header={
                        'backgroundColor': 'white',
                        'fontWeight': 'bold'
                    },
                    page_size=20,
                    style_cell={
                        'whiteSpace': 'normal',
                        'minWidth': '0px', 'maxWidth': '180px',
                    },

                    columns=[{"name": "Question Value", "id": "value"},
                             {"name": "Question", "id": "question"},
                             {"name": "Answer", "id": "answer"},
                             {"name": "Category", "id": "Category Names"},
                             {"name": "Category ID", "id": "category_id"},
                             {"name": "Air Date", "id": "airdate"}],
                    data=[],
                    sort_action="custom",
                    sort_mode="multi",
                    sort_by=[],
                    row_selectable="multi",
                    row_deletable=True,
                    selected_rows=[],
                    page_action='native',
                    page_current=0,
                ),
            ),
            html.Div(id='intermediate-value', style={'display': 'none'}),
            html.Button(id='submit-button2', n_clicks=0, children='Add selected questions to favorites'),
        ]),

        dcc.Tab(label="Your Favorite Questions", children=[
            html.Div(
                dash_table.DataTable(
                    id='datatable2',
                    style_cell={
                        'whiteSpace': 'normal',
                        'height': 'auto',
                        'minWidth': '0px', 'maxWidth': '180px'
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
                    page_action="native",
                    page_current=0,
                ),
            ),
        ]),

        dcc.Tab(label="Play Jeopardy!", children=[
            dbc.Button("Click To Start A New Game", color="primary", id='play-button'),
            html.Div(id='table-div', children=[

            ]),
            html.Div(id="score", children=200),
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


@app.callback([Output('datatable', 'data'), Output('datatable', 'selected_rows')],
              [Input('submit-button', 'n_clicks')],
              [State('clue-value', 'value'),
               State('category-value', 'value'),
               State('min-date', 'value'),
               State('max-date', 'value'),
               State('num-clues', 'value')])
def generate_table(n_clicks, input1, input2, input3, input4, input5):
    list_of_matching_ids = []
    table_data = []

    if input2 is not None:
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

        return data.to_dict(orient='records'), []

    elif input1 is not None or input3 is not None or input4 is not None:

        offset = 0
        finalData = make_api_call(input1, input2, input3, input4, offset)

        if input5 is not None:
            num_clues = int(input5)
            while True:
                offset += 100
                if (num_clues > len(finalData)):
                    jsonResponse = make_api_call(input1, input2, input3, input4, offset)
                    print(jsonResponse)
                    finalData += jsonResponse
                else:
                    break
        data = pd.DataFrame.from_dict(finalData)
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
    Output('answers', 'children')],
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
                                id='answer' + str(i)
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
                        hide_arrow=True
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
    [Output('popover0', 'style'), Output('popover-target0', 'style'),
     Output('popover1', 'style'), Output('popover-target1', 'style'),
     Output('popover2', 'style'), Output('popover-target2', 'style'),
     Output('popover3', 'style'), Output('popover-target3', 'style'),
     Output('popover4', 'style'), Output('popover-target4', 'style'),
     Output('popover5', 'style'), Output('popover-target5', 'style'),
     Output('popover6', 'style'), Output('popover-target6', 'style'),
     Output('popover7', 'style'), Output('popover-target7', 'style'),
     Output('popover8', 'style'), Output('popover-target8', 'style'),
     Output('popover9', 'style'), Output('popover-target9', 'style'),
     Output('popover10', 'style'), Output('popover-target10', 'style'),
     Output('popover11', 'style'), Output('popover-target11', 'style'),
     Output('popover12', 'style'), Output('popover-target12', 'style'),
     Output('popover13', 'style'), Output('popover-target13', 'style'),
     Output('popover14', 'style'), Output('popover-target14', 'style'),
     Output('popover15', 'style'), Output('popover-target15', 'style'),
     Output('popover16', 'style'), Output('popover-target16', 'style'),
     Output('popover17', 'style'), Output('popover-target17', 'style'),
     Output('popover18', 'style'), Output('popover-target18', 'style'),
     Output('popover19', 'style'), Output('popover-target19', 'style'),
     Output('popover20', 'style'), Output('popover-target20', 'style'),
     Output('popover21', 'style'), Output('popover-target21', 'style'),
     Output('popover22', 'style'), Output('popover-target22', 'style'),
     Output('popover23', 'style'), Output('popover-target23', 'style'),
     Output('popover24', 'style'), Output('popover-target24', 'style'),
        Output('score', 'children'), Output('used-buttons', 'children')
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
     State('score', 'children'),
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
    print(ctx.states)
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
        currentScore  = update_score(answer8, buttonNum, answers, currentScore)
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

    for i in range(0,25):
        if i not in usedButtons:
            outputList.append({'display': 'inline'})
            outputList.append({
                            'textAlign': 'center',
                            'color': '#FFCC00',
                            'font-weight': 'bold',
                            'font-size': '16px'
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
            output+=buttonNum[i]
    return int(output)

def update_score(answer, buttonNum, answers, currentScore):
    if answer == answers[buttonNum]:
        if (buttonNum <= 4):
            currentScore+=200
        elif buttonNum<=9:
            currentScore+=400
        elif buttonNum<=14:
            currentScore+=600
        elif buttonNum<=19:
            currentScore+=800
        elif buttonNum<=24:
            currentScore+=1000
    else:
        if (buttonNum <= 4):
            currentScore-=200
        elif buttonNum<=9:
            currentScore-=400
        elif buttonNum<=14:
            currentScore-=600
        elif buttonNum<=19:
            currentScore-=800
        elif buttonNum<=24:
            currentScore-=1000
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

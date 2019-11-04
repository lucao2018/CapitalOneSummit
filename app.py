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

# setup postgreSQL database with SQL Alchemy
server.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://flaehrpkwiurco:ad15ed7406fa968214c230eca578ba837934200' \
                                           '15f135cb9b34409da1b3e51c6@ec2-54-235-180-123.compute-1.amazonaws.com:' \
                                           '5432/d5ovqc3h4eto64'
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(server)


class JeopardyTable(db.Model):
    """ Creates a mapped class for the postgreSQL database with two columns, category name and category id
    """

    __tablename__ = 'jeopardy'
    category = db.Column(db.String)
    category_id = db.Column(db.Integer, primary_key=True)

    def __init__(self, category, category_id):
        self.category = category
        self.category_id = category_id

    def make_category_call(self, offset):
        """ Makes a call to /api/categories and returns the json of the response

        Parameters:
        offset (int): offset for call

        Returns:
        json: a json of the response returned from the api call

        """
        parameters = {
            "count": 100,
            "offset": offset
        }
        response = requests.get("http://jservice.io/api/categories/", params=parameters)
        return response.json()

    def populate_database(self):
        """ Function that is used to populate the PostgreSQL database with all available categories and their ids

        """
        offset = 0

        while True:
            response = self.make_category_call(offset)
            if len(response) == 0:
                break
            for item in response:
                category_id = item['id']
                category_title = item['title']
                if category_id is not None and category_title is not None:
                    if db.session.query(JeopardyTable).filter(JeopardyTable.category_id == category_id).count() == 0:
                        data = JeopardyTable(category_title, category_id)
                        db.session.add(data)
                        db.session.commit()
            offset += 100


# Layout for web app
app.layout = html.Div(children=[
    dcc.Tabs(id="tabs", children=[
        dcc.Tab(label='Search for Jeopardy Questions', children=[
            html.Div(children=[
                html.Div([
                    html.Br(),
                    html.H2(children="Jeopardy Trivia Search Engine", style={
                        'textAlign': 'center',
                    }),
                    html.Br(),
                    html.Div(id='search', children=[
                        html.Div([
                            html.Div(children=[
                                html.H6(children="Search for a category by key word/phrase (required)", style={
                                    'margin-left': '1em'
                                })
                            ], style={
                                'display': 'flex',
                                'justify-content': 'center'
                            }),
                            html.Div(children=[
                                dbc.Input(id='category-value',
                                          type='text',
                                          style={
                                              'margin-left': '1em',
                                              'width': '300px',
                                          },
                                          placeholder="Potpourri",
                                          )
                            ], style={
                                'display': 'flex',
                                'justify-content': 'center'
                            }),
                            html.Br(),
                            html.Div(
                                children=[html.H6("Type in the value of the clue in dollars: ",
                                                  style={
                                                      'margin-left': '1em'
                                                  })
                                          ], style={
                                    'display': 'flex',
                                    'justify-content': 'center'
                                }),
                            html.Div(children=[
                                dbc.Input(
                                    id='clue-value',
                                    style={
                                        'margin-left': '1em',
                                        'width': '300px'
                                    },
                                    placeholder=200,
                                    type="number"
                                ),
                            ], style={
                                'display': 'flex',
                                'justify-content': 'center'
                            }),
                            html.Br(),
                            html.Div(children=[
                                html.H6("Type in the range of dates that you would like to see clues from: ",
                                        style={
                                            'margin-left': '1em'
                                        })
                            ], style={
                                'display': 'flex',
                                'justify-content': 'center'
                            }),

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
                            html.Div(children=[html.H6("How many clues would you like be returned",
                                                       style={
                                                           'margin-left': '1em'
                                                       })
                                               ], style={
                                'display': 'flex',
                                'justify-content': 'center'
                            }),

                            html.Div(children=[
                                dbc.Input(
                                    id='num-clues',
                                    type='number',
                                    style={
                                        'margin-left': '1em',
                                        'width': '300px'
                                    },
                                    placeholder=100
                                )],
                                style={
                                    'display': 'flex',
                                    'justify-content': 'center'
                                }),
                        ]),
                    ], style={
                        'display': 'flex',
                        'justify-content': 'center',
                    }),
                    html.Br(),
                    html.Div(children=[
                        dbc.Button(id='submit-button', n_clicks=0, children='Search',
                                   style={
                                       'margin-left': '1em'
                                   },
                                   color='primary'),
                    ], style={
                        'display': 'flex',
                        'justify-content': 'center'
                    }),
                ]),

                html.Br(),
                html.Div(id='datatable-div', children=[
                ]),
                html.Br(),
                html.Div(id='favorites-button-div', children=[
                ]),
                html.Div(id='intermediate-value', style={
                    'display': 'none'
                }),
            ])
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
                        'fontWeight': 'bold',
                        'text-align': 'center'
                    },
                    page_size=20,
                    style_cell={
                        'whiteSpace': 'normal',
                        'minWidth': '0px', 'maxWidth': '280px',
                    },
                    style_cell_conditional=[
                        {'if': {'column_id': 'value'},
                         'width': '100px'},
                        {'if': {'column_id': 'category_id'},
                         'width': '30px'},
                        {'if': {'column_id': 'Category Name'},
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
                             {"name": "Category", "id": "category_names"},
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
            html.Div(id='play-div', children=[
                dbc.Button("Click To Start A New Game", id='play-button', color="primary"),
            ], style={
                'display': 'flex',
                'justify-content': 'center',
                'align-items': 'center',
                'padding-top': '50px'
            }),
            html.Div(children=[
            ]),
            html.Div(id='answers', style={'display': 'none'}),
            html.Div(id='used-buttons', style={'display': 'none'}, children=[
            ]),
            html.Div(id='correctness', children=[])
        ])
    ])
])


@app.callback([Output('datatable-div', 'children'), Output('favorites-button-div', 'children')],
              [Input('submit-button', 'n_clicks')],
              [State('clue-value', 'value'),
               State('category-value', 'value'),
               State('min-date', 'value'),
               State('max-date', 'value'),
               State('num-clues', 'value')])
def generate_table(n_clicks, clue_value, category_value, min_date, max_date, num_clues):
    """ Returns a dash datatable with clues that meet search criterion.

    Parameters:
        n_clicks (int): Number of times button has been clicked
        clue_value (int): Value of clue to search for in dollars
        category_value (str): Keyword/phrase to search for
        min_date (date): minimum date of clues to return
        max_date(date): maximum date of clues to return
        num_clues(int): number of clues to return

    Returns:
        dash datatable populated with information of matching clues or a dash bootstrap component alert
        warning that a required field was not filled out/field was filled out incorrectly

    """
    list_of_matching_ids = []
    table_data = []

    # If the user has not inputted a key word/phrase to search for, prevent search and alert them
    if n_clicks != 0:
        if category_value is None or category_value == "":
            return dbc.Alert("A required field was not filled out", color="danger", dismissable=True), []
        else:

            category_value = str(category_value)
            category_value = category_value.lower()

            # Make a query in PostgreSQL database with key word
            list_of_matches = JeopardyTable.query.filter(JeopardyTable.category.contains(category_value)).all()

            # Case for no results found
            if len(list_of_matches) == 0:
                return dbc.Alert("No results found", color="warning", dismissable=True), []

            # Store matching category ids and use them to make API calls and populate data table
            for category in list_of_matches:
                list_of_matching_ids.append(category.category_id)
            for id in list_of_matching_ids:
                if num_clues is not None:
                    if len(table_data) >= int(num_clues):
                        break
                if min_date == "":
                    min_date = None
                if max_date == "":
                    max_date = None

                # Validate user input for date format
                if min_date is None and max_date is not None:
                    min_date = '02/08/1985'

                if max_date is None and min_date is not None:
                    max_date = '01/01/9999'

                try:
                    json_response = make_api_call(clue_value, id, min_date, max_date, 0)
                    for item in json_response:
                        item['answer'] = item['answer'].replace("<i>", "")
                        item['answer'] = item['answer'].replace("</i>", "")

                    table_data += json_response
                except:
                    return dbc.Alert("Format for an input was invalid", color="danger", dismissable=True), []

            # return warning if no results found
            if len(table_data) == 0:
                return dbc.Alert("No results found", color="warning", dismissable=True), []

            for item in table_data:

                #extract date in mm-yyyy-dd format
                item['airdate'] = (item['airdate'])[0:10]

            data = pd.DataFrame.from_dict(table_data)

            # get the names of the categories and add to our data dict
            category_names = []

            for item in data['category']:
                category_names.append(item['title'])
            data['category_names'] = category_names

            return [dash_table.DataTable(
                id='datatable',
                style_table={
                    'width': '97.5%',
                    'margin-left': 'auto',
                    'margin-right': 'auto',
                },
                style_header={
                    'backgroundColor': 'white',
                    'fontWeight': 'bold',
                    'text-align': 'center'
                },
                page_size=20,
                style_cell={
                    'whiteSpace': 'normal',
                    'minWidth': '0px', 'maxWidth': '280px',
                },
                style_cell_conditional=[
                    {'if': {'column_id': 'value'},
                     'width': '100px'},
                    {'if': {'column_id': 'category_id'},
                     'width': '30px'},
                    {'if': {'column_id': 'category_names'},
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
                         {"name": "Category", "id": "category_names"},
                         {"name": "Category ID", "id": "category_id"},
                         {"name": "Air Date", "id": "airdate"}],
                data=data.to_dict(orient='records'),
                row_selectable="multi",
                row_deletable=True,
                selected_rows=[],
                page_action='native',
                page_current=0,
            ),
                dbc.Button(id='favorites-button', n_clicks=0, children='Save To Favorites', color="primary", style={
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
def start_jeopardy(n_clicks):
    """ Returns a dash bootstrap component table which will be the game board for the Jeopardy simulation. Also returns
    the list of answers (in Dash, information is passed between callbacks via hidden divs). Also returns a
    button/badge to keep track of the score

    Parameters:
        n_clicks (int): Number of times play-button was clicked

    Returns:
        dbc.Table: table that will represent the game board
        list: list of answers to questions
        html.Div: div that contains a button and badge to represent the player's score

    """

    if n_clicks is None:
        raise PreventUpdate
    else:

        # create an instance of the JeopardyGame object and use it to generate categories, clues, and answers
        game = JeopardyGame()
        questions = game.get_questions()
        answers = game.get_answers()
        categories = game.get_categories()

        # generate table headers (the categories)
        headers = []
        for category in categories:
            headers.append(html.Td(category, style={
                'width': '20px',
                'height': '100px',
                'vertical-align': 'middle'
            }))

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

        # generate buttons which will cause a modal with a clue to popup when clicked
        for i in range(0, 25):
            if i % 5 == 0:
                clue_value += 200
            row_list.append(
                html.Td(children=[html.Div([
                    html.A([
                        dbc.Button(html.U('$' + str(clue_value), style={
                            'color': '#FFCC00',
                            'font-weight': 'bold',
                            'font-size': '20px'
                        }), color="link", id="modal-button" + str(i))
                    ]),
                    dbc.Modal(
                        [
                            dbc.ModalHeader(questions[i]),
                            dbc.ModalBody("What is/are ...."),
                            dbc.ModalFooter([
                                dbc.Input(id='answer' + str(i)),
                                dbc.Button("Submit", id="check-question-button" + str(i),
                                           className="ml-auto" + str(i), color='primary'),
                            ]

                            ),
                        ],
                        id="modal" + str(i), backdrop=True),
                ])], style={
                    'width': '20%',
                    'height': '80px',
                    'text-align': 'center',
                    'vertical-align': 'middle'
                }))

        row1 = html.Tr(row_list[0:5], style={
            'text-align': 'center',
            'vertical-align': 'center'
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


# The following callbacks all toggle their corresponding modals so that when the user clicks on a value in a category
# column, the corresonding modal pops up
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


@app.callback(Output('datatable2', 'data'),
              [Input('favorites-button', 'n_clicks')],
              [State('datatable', 'selected_rows'),
               State('datatable2', 'data'),
               State('datatable', 'data')])
def store_favorites(n_clicks, selected_rows, existing_favorites, data):
    """ Stores selected favorite questions into the table in the favorites tab
    Parameters:
        n_clicks (int):Number of times the save to favorites button has been clicked
        existing_favorites (list): List of clues already added to favorites
        data (list): list of data from search table

    Returns:
        favorites_list (list): list of favorites that the user has saved

    """
    favorites_list = existing_favorites
    for selected_row in selected_rows:
        if data[selected_row] not in favorites_list:
            favorites_list.append(data[selected_row])
    return favorites_list


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
     Output('modal11', 'style'), Output('modal-button11', 'style'),
     Output('modal10', 'style'), Output('modal-button10', 'style'),
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
     Output('score-button', 'children'), Output('used-buttons', 'children'), Output('correctness', 'children')],
    [Input("check-question-button0", "n_clicks"), Input("check-question-button1", "n_clicks"),
     Input("check-question-button2", "n_clicks"), Input("check-question-button3", "n_clicks"),
     Input("check-question-button4", "n_clicks"), Input("check-question-button5", "n_clicks"),
     Input("check-question-button6", "n_clicks"), Input("check-question-button7", "n_clicks"),
     Input("check-question-button8", "n_clicks"), Input("check-question-button9", "n_clicks"),
     Input("check-question-button10", "n_clicks"), Input("check-question-button11", "n_clicks"),
     Input("check-question-button12", "n_clicks"), Input("check-question-button13", "n_clicks"),
     Input("check-question-button14", "n_clicks"), Input("check-question-button15", "n_clicks"),
     Input("check-question-button16", "n_clicks"), Input("check-question-button17", "n_clicks"),
     Input("check-question-button18", "n_clicks"), Input("check-question-button19", "n_clicks"),
     Input("check-question-button20", "n_clicks"), Input("check-question-button21", "n_clicks"),
     Input("check-question-button22", "n_clicks"), Input("check-question-button23", "n_clicks"),
     Input("check-question-button24", "n_clicks")],
    [State('answer0', 'value'), State('answer1', 'value'), State('answer2', 'value'),
     State('answer3', 'value'), State('answer4', 'value'), State('answer5', 'value'),
     State('answer6', 'value'), State('answer7', 'value'), State('answer8', 'value'),
     State('answer9', 'value'), State('answer10', 'value'), State('answer11', 'value'),
     State('answer12', 'value'), State('answer13', 'value'), State('answer14', 'value'),
     State('answer15', 'value'), State('answer16', 'value'), State('answer17', 'value'),
     State('answer18', 'value'), State('answer19', 'value'), State('answer20', 'value'),
     State('answer21', 'value'), State('answer22', 'value'), State('answer23', 'value'),
     State('answer24', 'value'), State('score-button', 'children'), State('answers', 'children'),
     State('used-buttons', 'children')])
def check_answer(n_clicks0, n_clicks1, n_clicks2, n_clicks3, n_clicks4, n_clicks5, n_clicks6, n_clicks7, n_clicks8,
                 n_clicks9, n_clicks10, n_clicks11, n_clicks12, n_clicks13, n_clicks14, n_clicks15, n_clicks16,
                 n_clicks17, n_clicks18, n_clicks19, n_clicks20, n_clicks21, n_clicks22, n_clicks23, n_clicks24,
                 answer0, answer1, answer2, answer3, answer4, answer5, answer6, answer7, answer8, answer9, answer10,
                 answer11, answer12, answer13, answer14, answer15, answer16, answer17, answer18, answer19, answer20,
                 answer21, answer22, answer23, answer24, current_score, answers, used_buttons):
    """ Since dash does not allow multiple callbacks to have the same output, I unfortunately had to use one function
        to check answers submitted to any of the questions. This function uses dash callback context to determine which
        submit button was pressed. It then checks if the answer is the same as with the answer stored in the index
        of the button number in the answer list and updates the score accordingly

    Parameters:
        n_clicks0-n_clicks24 (int):Number of times corresponding submit-button was clicked
        answer0-answer24 (string): Answer that user submitted for a question

    Returns:
        output_list (list): a list containing various data types that is used to hide answered questions and update
        the score

    """

    # Use dash callback context to find out which submit button was pressed
    ctx = dash.callback_context

    # Extract button number
    button_num = ctx.triggered[0]['prop_id'].split('.')[0]
    button_num = extract_num(button_num)

    old_score = current_score

    # Check which button was pressed and update the current score based on whether or not the answer was correct
    if button_num == 0:
        current_score = update_score(answer0, button_num, answers, current_score)
    elif button_num == 1:
        current_score = update_score(answer1, button_num, answers, current_score)
    elif button_num == 2:
        current_score = update_score(answer2, button_num, answers, current_score)
    elif button_num == 3:
        current_score = update_score(answer3, button_num, answers, current_score)
    elif button_num == 4:
        current_score = update_score(answer4, button_num, answers, current_score)
    elif button_num == 5:
        current_score = update_score(answer5, button_num, answers, current_score)
    elif button_num == 6:
        current_score = update_score(answer6, button_num, answers, current_score)
    elif button_num == 7:
        current_score = update_score(answer7, button_num, answers, current_score)
    elif button_num == 8:
        current_score = update_score(answer8, button_num, answers, current_score)
    elif button_num == 9:
        current_score = update_score(answer9, button_num, answers, current_score)
    elif button_num == 10:
        current_score = update_score(answer10, button_num, answers, current_score)
    elif button_num == 11:
        current_score = update_score(answer11, button_num, answers, current_score)
    elif button_num == 12:
        current_score = update_score(answer12, button_num, answers, current_score)
    elif button_num == 13:
        current_score = update_score(answer13, button_num, answers, current_score)
    elif button_num == 14:
        current_score = update_score(answer14, button_num, answers, current_score)
    elif button_num == 15:
        current_score = update_score(answer15, button_num, answers, current_score)
    elif button_num == 16:
        current_score = update_score(answer16, button_num, answers, current_score)
    elif button_num == 17:
        current_score = update_score(answer17, button_num, answers, current_score)
    elif button_num == 18:
        current_score = update_score(answer18, button_num, answers, current_score)
    elif button_num == 19:
        current_score = update_score(answer19, button_num, answers, current_score)
    elif button_num == 20:
        current_score = update_score(answer20, button_num, answers, current_score)
    elif button_num == 21:
        current_score = update_score(answer21, button_num, answers, current_score)
    elif button_num == 22:
        current_score = update_score(answer22, button_num, answers, current_score)
    elif button_num == 23:
        current_score = update_score(answer23, button_num, answers, current_score)
    elif button_num == 24:
        current_score = update_score(answer24, button_num, answers, current_score)

    # List that keeps track of which questions have already been attempted
    used_buttons.append(button_num)
    output_list = []

    # Populate a list that will be used to hide questions who have already been attempted
    for i in range(0, 25):
        if i not in used_buttons:
            output_list.append({})
            output_list.append({
                'color': '#FFCC00',
                'font-weight': 'bold'
            })
        else:
            output_list.append({'display': 'none'})
            output_list.append({'display': 'none'})

    output_list.append(current_score)
    output_list.append(used_buttons)

    # if the user gets it wrong, tell them what the correct answer is with an alert
    if current_score < old_score:
        output_list.append(dbc.Alert("That is incorrect. The correct answer is: " +
                                     answers[button_num] + ".", color="danger", dismissable=True,
                                     style={
                                         'position': 'fixed',
                                         'top': '50%',
                                         'left': '50%',
                                         'transform': 'translate(-50%, -50%)',
                                         'height': '300px',
                                         'width': '400px',
                                         'z - index': '10',
                                         'font-size': '30px',
                                     }))
    else:
        output_list.append([])

    return output_list


def make_api_call(clue_value, category_ID, min_date, max_date, offset):
    """ Makes call to /api/clues and returns json of response.

    Parameters:
        clue_value (int): Value of clues to search for
        category_ID(int): Category id of clues to search for
        min_date (date): minimum date of clues to return
        max_date(date): maximum date of clues to return
        offset(int): offset of dates to return

    Returns:
        json of response

    """
    parameters = {
        "value": clue_value,
        "category": category_ID,
        "min_date": parse_date(min_date),
        "max_date": parse_date(max_date),
        "offset": offset
    }
    response = requests.get("http://jservice.io/api/clues/", params=parameters)
    return response.json()


def extract_num(button_num):
    """ Extracts the button number from a string

    Parameters:
        button_num (str): A string representing the id of the submit button pressed

    Returns:
        integer matching the button number

    """
    output = ""
    for i in range(len(button_num)):
        if button_num[i].isdigit():
            output += button_num[i]
    return int(output)


def update_score(answer, button_num, answers, current_score):
    """ Updates a user's score by checking if their answer to a question is correct

    Parameters:
        answer (str): A string representing the user's submitted answer
        button_num (int): integer corresponding with the pressed submit button
        answers (list): A list with all of the correct answers
        current_score (int): The user's current score

    Returns:
        integer matching the button number

    """

    if answer.lower() == answers[button_num].lower():
        if button_num <= 4:
            current_score += 200
        elif button_num <= 9:
            current_score += 400
        elif button_num <= 14:
            current_score += 600
        elif button_num <= 19:
            current_score += 800
        elif button_num <= 24:
            current_score += 1000
    else:
        if button_num <= 4:
            current_score -= 200
        elif button_num <= 9:
            current_score -= 400
        elif button_num <= 14:
            current_score -= 600
        elif button_num <= 19:
            current_score -= 800
        elif button_num <= 24:
            current_score -= 1000
    return current_score


def parse_date(date_string):
    """ Returns a string converted to a date.

    Parameters:
        date_string (str): The string which is to be converted

    Returns:
        datetime_obj: The converted date

    """
    if date_string is None:
        return None

    format_str = '%m/%d/%Y'
    datetime_obj = datetime.datetime.strptime(date_string, format_str)
    return datetime_obj


if __name__ == '__main__':
    app.run_server(debug=True)

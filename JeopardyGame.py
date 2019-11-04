import requests
import random


class JeopardyGame(object):
    """
    A class used to represent a game of jeopardy
    ...

    Attributes
    ----------
    category_ids : list
        a list containing all of the category ids used in the game
    category_titles: list
        a list containing all of the category titles

    Methods
    -------
    generate_categories()
        method that generates a list of categories used in the game

    valid_category(id)
        method that makes sure a category is valid (has clues with values 200, 400, 600, 800, 1000)

    generate_category_titles()
        method that generates a list of category names used in the game

    generate_questions()
        method that generates a list of questions used in the game

    get_answers():
        method that returns the list of answers

    get_questions():
        method that returns a list of questions

    get_categories():
        method that returns a list of categories
    """

    def __init__(self):
        self.category_ids = []
        self.category_titles = []
        self.questions = []
        self.answers = []

        self.generate_categories()
        self.generate_category_titles()
        self.generate_questions()

    def generate_categories(self):
        """Updates self.category_ids with categories used in the game by calling /api/random/
        """
        parameters = {
            "count": 1
        }

        # populates self.category_ids with clues from 5 randomly generated, valid categories
        while len(self.category_ids) < 5:
            response = requests.get("http://jservice.io/api/random/", params=parameters)
            data = response.json()
            id = data[0]['category_id']
            if self.validate_category(id):
                self.category_ids.append(id)

    def validate_category(self, id):
        """returns a boolean indicating whether a category is valid by calling /api/clues to get information about the
        category
        """
        parameters = {
            "category": id,
        }
        response = requests.get("http://jservice.io/api/clues/", params=parameters)
        data = response.json()
        list_of_values = []
        for item in data:
            list_of_values.append(item['value'])

        # makes sure category has proper values
        if 200 not in list_of_values or 400 not in list_of_values or 600 not in list_of_values or 800 not in \
                list_of_values or 1000 not in list_of_values:
            return False
        else:
            return True


    def generate_category_titles(self):
        """returns a boolean indicating whether a category is valid by calling /api/category to get information about
        the category
        """
        for id in self.category_ids:
            parameters = {
                "id": id,
            }
            response = requests.get("http://jservice.io/api/category", params=parameters)
            data = response.json()
            self.category_titles.append(data['title'])

    def generate_questions(self):
        """Update self.questions and self.answers to have questions and answers used in the game by calling /api/clues/
        """
        total_list_of_clues = []
        total_list_of_answers = []

        # generates clues from the 5 randomly generated categories
        for i in range(200, 1001, 200):
            for id in self.category_ids:
                parameters = {
                    "category": id,
                    "value": i
                }
                response = requests.get("http://jservice.io/api/clues/", params=parameters)
                data = response.json()
                random_clue_index = random.randint(0, len(data) - 1)
                total_list_of_clues.append(data[random_clue_index]['question'])
                answer = data[random_clue_index]['answer']
                answer = answer.replace("<i>", "")
                answer = answer.replace("</i>", "")
                total_list_of_answers.append(answer)

        self.questions = total_list_of_clues
        self.answers = total_list_of_answers

    def get_questions(self):
        """returns game questions
        """
        return self.questions

    def get_answers(self):
        """returns game answers
        """
        return self.answers

    def get_categories(self):
        """returns game categories
        """
        return self.category_titles

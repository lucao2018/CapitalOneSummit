import requests
import random


class JeopardyGame(object):

    def __init__(self):
        self.score = 0
        self.category_ids = []
        self.category_titles = []
        self.questions = []
        self.answers = []

    def generate_categories(self):
        parameters = {
            "count": 1
        }

        while len(self.category_ids) < 5:
            response2 = requests.get("http://jservice.io/api/random/", params=parameters)
            data = response2.json()
            id = data[0]['category_id']
            if self.validate_category(id):
                self.category_ids.append(id)

    def validate_category(self, id):
        parameters = {
            "category": id,
        }
        response = requests.get("http://jservice.io/api/clues/", params=parameters)
        data = response.json()
        list_of_values = []
        for item in data:
            list_of_values.append(item['value'])
        if 200 not in list_of_values or 400 not in list_of_values or 600 not in list_of_values or 800 not in list_of_values or 1000 not in list_of_values:
            return False
        else:
            return True

    def generate_category_titles(self):
        for id in self.category_ids:
            parameters = {
                "id": id,
            }
            response = requests.get("http://jservice.io/api/category", params=parameters)
            data = response.json()
            self.category_titles.append(data['title'])

    def generate_questions(self):
        total_list_of_clues = []
        total_list_of_answers = []

        for i in range(200, 1001, 200):
            for id in self.category_ids:
                parameters = {
                    "category": id,
                    "value": i
                }
                response = requests.get("http://jservice.io/api/clues/", params=parameters)
                data = response.json()
                randomClueIndex = random.randint(0, len(data) - 1)
                total_list_of_clues.append(data[randomClueIndex]['question'])
                total_list_of_answers.append(data[randomClueIndex]['answer'])

        self.questions = total_list_of_clues
        self.answers = total_list_of_answers

    def get_questions(self):
        return self.questions

    def get_answers(self):
        return self.answers

    def get_categories(self):
        return self.category_titles

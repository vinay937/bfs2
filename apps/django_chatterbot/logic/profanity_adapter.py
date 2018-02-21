from chatterbot.conversation import Statement
from chatterbot.logic import BestMatch
from django.conf import settings
import random


class ProfanityAdapter(BestMatch):
	default_responses = ['What did I do wrong?!',
					'You have been reported',
					"You're upbringing sucks",
					"Muh dhoke aa BC"]

	def __init__(self, **kwargs):
		super(ProfanityAdapter, self).__init__(**kwargs)
		self.response_list = [
            Statement(text=default) for default in self.default_responses
        ]

	def can_process(self, statement):
		return True

	def process(self, statement):
		confidence = 0
		closest_match = self.get(statement)

		with open(settings.ABUSE_FILE, 'r') as f:
			abuses = [line.rstrip('\n') for line in f]

		if any(x in abuses for x in statement.text.split()):
			confidence = 2

		response = self.select_response(statement, self.response_list)

		if closest_match.confidence > confidence:
			response.confidence = 0
		else:
			response.confidence = confidence

		return response
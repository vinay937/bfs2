from chatterbot.conversation import Statement
from chatterbot.logic import BestMatch
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import validate_email


import random


class UserAdapter(BestMatch):
	"""
	Checks for abuses in the statement and accordingly gives a defalut response related to it
	"""

	def __init__(self, **kwargs):
		super(UserAdapter, self).__init__(**kwargs)

	def can_process(self, statement):
		return True

	def process(self, statement):
		confidence = 0
		closest_match = self.get(statement)
		user = None

		try:
			validate_email(statement.text)
			valid_email = True
		except:
			valid_email = False

		if valid_email:
			confidence = 2
			try:
				user = get_user_model().objects.get(email=statement.text)
			except get_user_model().DoesNotExist:
				user = None
		else:
			try:
				user = get_user_model().objects.filter(first_name__icontains=statement.text)
				print(user)
			except get_user_model().DoesNotExist:
				user = None
		
		if user:
			if len(user) > 1:
				txt = ''
				for u in user:
					print(u)
					txt += 'Name : ' + u.first_name + '<br>' + 'Username : ' + u.username + '<br>'
				response = Statement('More than one results obtained: <br>' + txt)
				confidence = 2
			else:
				response = Statement('You are {} <br> Your username to log in is {}.'.format(user.first_name, user.username))
				confidence = 2
		else:
			response = Statement('A man has no name')

		response.confidence = confidence

		return response
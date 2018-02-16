from django.db import models
from django.contrib.auth import get_user_model

class FeedbackForm(models.Model):
	'''
	Feedback Form: Stores the feedback form for the respective type of user
	As each type of user has different forms to be displayed, we store the below boolean values
	'''
	title = models.CharField("Form Title", max_length=50)
	description = models.CharField("Form Description", max_length=250)

	student = models.BooleanField(default=False)
	faculty = models.BooleanField(default=False)
	hod = models.BooleanField(default=False)
	vice_principal = models.BooleanField(default=False)
	principal = models.BooleanField(default=False)

	def __str__(self):
		return self.title


class Question(models.Model):
	'''
	Question: Holds the questions for respective user type
	'''
	form = models.ForeignKey('FeedbackForm', on_delete=models.CASCADE)
	text = models.TextField("Question")

	def __str__(self):
		return self.question


class Answer(models.Model):
	'''
	Answers: If the student is giving the feedback for a teacher, it gets stored for the teacher,
	wchich holds the details from the table - teaches. So, we can obtain all details such as Sem, Sec 
	from it while generation of reports.

	If the feedback is to anyone else, it will get stored to the User. 
	'''
	question = models.ForeignKey('question')
	teacher = models.ForeignKey('general.teaches', null=True)

	ANSWER_CHOICES = [('Excellent','Excellent'), ('Good','Good'), ('Satisfactory','Satisfactory'), ('Poor', 'Poor'), ('Very Poor', 'Very Poor')]
	value = models.CharField(max_length=50, choices=ANSWER_CHOICES)
	
	recipient = models.ForeignKey(get_user_model(), null=True)

	def __str__(self):
		return self.question.text

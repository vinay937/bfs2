from django.db import models
from django.contrib.auth import get_user_model


class FeedbackForm(models.Model):
    """
	Feedback Form: Stores the feedback form for the respective type of user
	As each type of user has different forms to be displayed, we store the below boolean values
	"""

    title = models.CharField("Form Title", max_length=50)
    description = models.CharField("Form Description", max_length=250)

    # The type of user that is allowed to give the feedback for this form
    user_type = models.ManyToManyField(
        "general.UserType",
        help_text="Type of user that is allowed to give the feedback for this form",
    )

    # The code of the form
    code = models.CharField(
        "Form Code",
        max_length=2,
        help_text="Mandatory to enter two charachters",
        null=False,
        blank=False,
    )

    # The type of the user that will receive feedback through this form
    recipient = models.ForeignKey(
        "general.UserType",
        help_text="Type of user that is receiving the feedback for this form",
        related_name="form",
        null=True,
    )

    active = models.BooleanField(default=True)

    # def __str__(self):
    # 	return self.title


class Question(models.Model):
    """
	Question: Holds the questions for respective user type
	"""

    form = models.ForeignKey(
        "FeedbackForm", on_delete=models.CASCADE, related_name="question"
    )
    text = models.TextField("Question")

    # def __str__(self):
    # 	return self.text


class Answer(models.Model):
    """
	Answers: If the student is giving the feedback for a teacher, it gets stored for the teacher,
	which holds the details from the table - teaches. So, we can obtain all details such as Sem, Sec
	from it while generation of reports.

	If the feedback is to anyone else, it will get stored to the User.
	"""

    question = models.ForeignKey("question")
    teacher = models.ForeignKey("general.teaches", null=True)

    ANSWER_CHOICES = [
        ("Excellent", "Excellent"),
        ("Good", "Good"),
        ("Satisfactory", "Satisfactory"),
        ("Poor", "Poor"),
        ("Very Poor", "Very Poor"),
    ]
    value = models.CharField(max_length=50, choices=ANSWER_CHOICES)

    form = models.ForeignKey("feedbackform", null=True)
    recipient = models.ForeignKey(get_user_model(), null=True)

    def __str__(self):
        return self.question.text


class StudentAnswer(models.Model):
    """
	Answers: If the student is giving the feedback for a teacher, it gets stored for the teacher,
	which holds the details from the table - teaches. So, we can obtain all details such as Sem, Sec
	from it while generation of reports.

	If the feedback is to anyone else, it will get stored to the User.
	"""

    question = models.ForeignKey("question")
    teacher = models.ForeignKey("general.teaches", null=True)

    ANSWER_CHOICES = [
        ("Excellent", "Excellent"),
        ("Good", "Good"),
        ("Satisfactory", "Satisfactory"),
        ("Poor", "Poor"),
        ("Very Poor", "Very Poor"),
    ]
    value = models.CharField(max_length=60, choices=ANSWER_CHOICES)

    form = models.ForeignKey("feedbackform", null=True)
    recipient = models.ForeignKey(get_user_model(), null=True)

    def __str__(self):
        return self.teacher.teacher.first_name


class ConsolidatedReport(models.Model):
    """
	The consolidated report is stored in this table.
	"""

    name = models.CharField("Name of faculty", max_length=100)
    form_name = models.CharField("Name of the form", max_length=100)
    total = models.CharField("Total value they got", max_length=10)
    department = models.CharField(
        "Department Code", max_length=30, null=True, blank=True
    )

    # def __str__(self):
    # 	return self.name


class StudentConsolidatedReport(models.Model):
    """
	The Student consolidated report is stored in this table.
	"""

    name = models.CharField("Name of faculty", max_length=100)
    total = models.FloatField("Total value they got", max_length=10)
    department = models.CharField(
        "Department Code", max_length=30, null=True, blank=True
    )
    teacher = models.ForeignKey("general.teaches", null=True)

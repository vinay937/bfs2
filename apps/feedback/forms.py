from django import forms
from .models import Answer
from django.forms import modelformset_factory

class HorizontalRadioSelect(forms.RadioSelect):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		css_style = 'style="display: inline-block; margin-right: 10px;"'

		self.renderer.inner_html = '<li ' + css_style + '>{choice_value}{sub_widgets}</li>'
		

class FeedbackAnswerForm(forms.ModelForm):
	choices = Answer.ANSWER_CHOICES
	answer = forms.ChoiceField(label="", choices=choices, widget=forms.RadioSelect(attrs={'class': 'inline', 'required':'required'}))
	class Meta:
		model = Answer
		fields = ('answer',)


AnswerFormSet = modelformset_factory(Answer, form=FeedbackAnswerForm)
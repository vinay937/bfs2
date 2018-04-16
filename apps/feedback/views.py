'''
Copyright 2017 DevX Labs
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
	http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from .models import Answer, FeedbackForm, ConsolidatedReport, StudentAnswer, StudentConsolidatedReport
from .forms import FeedbackAnswerForm, AnswerFormSet, StudentFeedbackAnswerForm

from apps.general.models import UserType, Teaches, User

import json
import random
from decimal import Decimal


class FeedbackView(FormView):

	template_name = 'feedback/entry.html'
	form_class = FeedbackAnswerForm

	def get_list(self, model, g_list):
		c_list = list()
		for pk in g_list:
			c_list.append(model.objects.get(pk=pk))
		return c_list

	def get_context_data(self, **kwargs):
		context = super(FeedbackView, self).get_context_data(**kwargs)

		recipients = self.request.session.get('recipients')

		if recipients:
			recipients = self.get_list(get_user_model(), recipients)

		post_recipients = self.request.session.get('post_recipients')
		if post_recipients:
			post_recipients = self.get_list(get_user_model(), post_recipients)


		# Student Form
		if self.request.user.is_student():
			self.form_class = StudentFeedbackAnswerForm
			self.template_name = "feedback/student_entry.html"
			recipients = self.request.session.get('recipients_theory')
			recipients = self.get_list(Teaches, recipients)
			lab_recipients = self.request.session.get('recipients_labs')
			lab_recipients = self.get_list(Teaches, lab_recipients)
			project_recipients = self.request.session.get('recipients_project')
			project_recipients = self.get_list(Teaches, project_recipients)

			theory_post_recipients = self.request.session.get('post_recipients_theory')
			theory_post_recipients = self.get_list(Teaches, theory_post_recipients)
			lab_post_recipients = self.request.session.get('post_recipients_labs')
			lab_post_recipients = self.get_list(Teaches, lab_post_recipients)
			project_post_recipients = self.request.session.get('post_recipients_project')
			project_post_recipients = self.get_list(Teaches, project_post_recipients)

			context['recipients_theory'] = recipients
			context['recipients_labs'] = lab_recipients
			context['recipients_project'] = project_recipients
			iterable_forms = self.request.session['form']
			iterable_forms = self.get_list(FeedbackForm, iterable_forms)

			theory_count = self.request.session['theory_count']
			lab_count = self.request.session['labs_count']
			project_count = self.request.session['project_count']
			context['form_recipients'] = self.request.session.get('form_recipients')

			if theory_count:
				if theory_post_recipients:
					recipients_name = theory_post_recipients[0]
					if self.request.user.is_student():
						feedback_form = FeedbackForm.objects.get(code='ST')
						question_count = feedback_form.question.all().count()
						StudentAnswerFormset = modelformset_factory(StudentAnswer, form=StudentFeedbackAnswerForm, extra=question_count)
						formset = StudentAnswerFormset(queryset=StudentAnswer.objects.none())
						context['formset'] = formset
						form_zip = zip(formset, feedback_form.question.all())
						context['form_zip'] = form_zip
						context['recipient_name'] = recipients_name
			elif lab_count:
				if lab_post_recipients:
					recipients_name = lab_post_recipients[0]
					if self.request.user.is_student():
						feedback_form = FeedbackForm.objects.get(code='SL')
						question_count = feedback_form.question.all().count()
						StudentAnswerFormset = modelformset_factory(StudentAnswer, form=StudentFeedbackAnswerForm, extra=question_count)
						formset = StudentAnswerFormset(queryset=StudentAnswer.objects.none())
						context['formset'] = formset
						form_zip = zip(formset, feedback_form.question.all())
						context['form_zip'] = form_zip
						context['recipient_name'] = recipients_name
			elif project_count:
				if project_post_recipients:
					recipients_name = project_post_recipients[0]
					if self.request.user.is_student():
						feedback_form = FeedbackForm.objects.get(code='SP')
						question_count = feedback_form.question.all().count()
						StudentAnswerFormset = modelformset_factory(StudentAnswer, form=StudentFeedbackAnswerForm, extra=question_count)
						formset = StudentAnswerFormset(queryset=StudentAnswer.objects.none())
						context['formset'] = formset
						form_zip = zip(formset, feedback_form.question.all())
						context['form_zip'] = form_zip
						context['recipient_name'] = recipients_name
			elif iterable_forms:
				feedback_form = iterable_forms[0]
				question_count = feedback_form.question.all().count()
				StudentAnswerFormset = modelformset_factory(StudentAnswer,
					form=StudentFeedbackAnswerForm, extra=question_count)
				formset = StudentAnswerFormset(queryset=StudentAnswer.objects.none())
				context['formset'] = formset
				form_zip = zip(formset, feedback_form.question.all())
				context['form_zip'] = form_zip
				context['form_recipient_name'] = feedback_form.recipient.name
			return context

		# Faculty feedback
		context['recipients'] = recipients

		count = self.request.session['count']

		iterable_forms = self.request.session['form']
		iterable_forms = self.get_list(FeedbackForm, iterable_forms)
		context['form_recipients'] = self.request.session.get('form_recipients')

		if count:
			if post_recipients:
				recipients_name = get_user_model().objects.get(username=post_recipients[0]).first_name
				if self.request.user.is_hod():
					feedback_form = FeedbackForm.objects.get(code='HH')
					question_count = feedback_form.question.all().count()
					AnswerFormset = modelformset_factory(Answer, form=FeedbackAnswerForm, extra=question_count)
					formset = AnswerFormset(queryset=Answer.objects.none())
					context['formset'] = formset
					form_zip = zip(formset, feedback_form.question.all())
					context['form_zip'] = form_zip
					context['recipient_name'] = recipients_name
				elif self.request.user.is_faculty():
					feedback_form = FeedbackForm.objects.get(code='FF')
					question_count = feedback_form.question.all().count()
					AnswerFormset = modelformset_factory(Answer, form=FeedbackAnswerForm, extra=question_count)
					formset = AnswerFormset(queryset=Answer.objects.none())
					context['formset'] = formset
					form_zip = zip(formset, feedback_form.question.all())
					context['form_zip'] = form_zip
					context['recipient_name'] = recipients_name
			elif iterable_forms:
				feedback_form = iterable_forms[0]
				question_count = feedback_form.question.all().count()
				AnswerFormset = modelformset_factory(Answer,
					form=FeedbackAnswerForm, extra=question_count)
				formset = AnswerFormset(queryset=Answer.objects.none())
				context['formset'] = formset
				form_zip = zip(formset, feedback_form.question.all())
				context['form_zip'] = form_zip
				context['form_recipient_name'] = feedback_form.recipient.name
		return context

	def get_user(self, type):
		user = get_user_model().objects.filter(user_type=type)
		if user.count() > 1:
			user = user.filter(department=self.request.user.department)
		return user[0]

	def post(self, request, *args, **kwargs):
		form_class = self.get_form_class()
		form = self.get_form(form_class)
		AnswerFormset = modelformset_factory(Answer, form=FeedbackAnswerForm)
		formset = AnswerFormset(request.POST)
		form_valid = form.is_valid()
		formset_valid = formset.is_valid()
		if self.request.user.is_student():
			StudentAnswerFormset = modelformset_factory(StudentAnswer, form=StudentFeedbackAnswerForm)
			formset = StudentAnswerFormset(request.POST)
			form_valid = form.is_valid()
			formset_valid = formset.is_valid()
			theory_count = self.request.session['theory_count']
			lab_count = self.request.session['labs_count']
			project_count = self.request.session['project_count']
			count = self.request.session['count']
			theory_recipients = self.request.session.get('post_recipients_theory')
			lab_recipients = self.request.session.get('post_recipients_labs')
			project_recipients = self.request.session.get('post_recipients_project')
			if theory_recipients:
				theory_recipients = self.get_list(Teaches, theory_recipients)
			if lab_recipients:
				lab_recipients = self.get_list(Teaches, lab_recipients)
			if project_recipients:
				project_recipients = self.get_list(Teaches, project_recipients)
			iterable_forms = self.request.session.get('form')
			if iterable_forms:
				iterable_forms = self.get_list(FeedbackForm, iterable_forms)
			if formset_valid:
				if count:
					if theory_count:
						if theory_recipients:
							teaches = Teaches.objects.get(pk=theory_recipients[0].pk)
							feedback_form = FeedbackForm.objects.get(code='ST')
							question = feedback_form.question.all()
							for form, que in zip(formset, question):
								ans = form.cleaned_data.get('answer')
								answer = StudentAnswer.objects.create(question=que,
										value=ans, teacher=teaches, form=feedback_form)
							del self.request.session['post_recipients_theory'][0]
							self.request.session['post_recipients_theory'] = self.request.session['post_recipients_theory']
							self.request.session['theory_count'] -= 1
					elif lab_count:
						if lab_recipients:
							teaches = Teaches.objects.get(pk=lab_recipients[0].pk)
							feedback_form = FeedbackForm.objects.get(code='SL')
							question = feedback_form.question.all()
							for form, que in zip(formset, question):
								ans = form.cleaned_data.get('answer')
								answer = StudentAnswer.objects.create(question=que,
										value=ans, teacher=teaches, form=feedback_form)
							del self.request.session['post_recipients_labs'][0]
							self.request.session['post_recipients_labs'] = self.request.session['post_recipients_labs']
							self.request.session['labs_count'] -= 1
					elif project_count:
						if project_recipients:
							teaches = Teaches.objects.get(pk=project_recipients[0].pk)
							feedback_form = FeedbackForm.objects.get(code='SP')
							question = feedback_form.question.all()
							for form, que in zip(formset, question):
								ans = form.cleaned_data.get('answer')
								answer = StudentAnswer.objects.create(question=que,
										value=ans, teacher=teaches, form=feedback_form)
							del self.request.session['post_recipients_project'][0]
							self.request.session['post_recipients_project'] = self.request.session['post_recipients_project']
							self.request.session['project_count'] -= 1
					elif iterable_forms:
						feedback_form = iterable_forms[0]
						question_count = feedback_form.question.all().count()
						for form, que in zip(formset, feedback_form.question.all()):
							ans = form.cleaned_data.get('answer')
							answer = StudentAnswer.objects.create(question=que,
									value=ans, recipient=self.get_user(feedback_form.recipient), form=feedback_form)
						# remove the forms once done
						del self.request.session['form'][0]
						self.request.session['form'] = self.request.session['form']
					self.request.session['count'] -= 1

			if request.session['count']:
				return HttpResponseRedirect(reverse_lazy('feedback_form'))
			else:
				self.request.user.done = True
				self.request.user.save()
				return HttpResponseRedirect(reverse_lazy('logout'))


		count = self.request.session['count']

		recipients = self.request.session.get('post_recipients')
		if recipients:
			recipients = self.get_list(get_user_model(), recipients)

		iterable_forms = self.request.session.get('form')
		if iterable_forms:
			iterable_forms = self.get_list(FeedbackForm, iterable_forms)

		if formset_valid:
			if count:
				if recipients:
					recipient = get_user_model().objects.get(pk=recipients[0].pk)
					if self.request.user.is_hod():
						feedback_form = FeedbackForm.objects.get(code='HH')
						question = feedback_form.question.all()
						for form, que in zip(formset, question):
							ans = form.cleaned_data.get('answer')
							answer = Answer.objects.create(question=que,
								value=ans, recipient=recipient, form=feedback_form)
					elif self.request.user.is_faculty():
						feedback_form = FeedbackForm.objects.get(code='FF')
						question = feedback_form.question.all()
						for form, que in zip(formset, question):
							ans = form.cleaned_data.get('answer')
							answer = Answer.objects.create(question=que,
								value=ans, recipient=recipient, form=feedback_form)

					del self.request.session['post_recipients'][0]
					self.request.session['post_recipients'] = self.request.session['post_recipients']

				elif iterable_forms:
					feedback_form = iterable_forms[0]
					question_count = feedback_form.question.all().count()
					for form, que in zip(formset, feedback_form.question.all()):
						ans = form.cleaned_data.get('answer')
						answer = Answer.objects.create(question=que,
								value=ans, recipient=self.get_user(feedback_form.recipient), form=feedback_form)

					# remove the forms once done
					del self.request.session['form'][0]
					self.request.session['form'] = self.request.session['form']

				# decrease the count
				self.request.session['count'] -= 1
		if request.session['count']:
			return HttpResponseRedirect(reverse_lazy('feedback_form'))
		else:
			self.request.user.done = True
			self.request.user.save()
			return HttpResponseRedirect(reverse_lazy('logout'))


class Report(TemplateView):
	template_name = "feedback/report.html"

	def get_context_data(self, *args, **kwargs):
		context = super(Report, self).get_context_data(*args, **kwargs)
		user_type = self.request.user.get_user_type()
		forms = FeedbackForm.objects.filter(recipient=user_type, active=True)
		results = dict()
		for form in forms:
			answers = Answer.objects.filter(form=form, recipient=self.request.user)
			results[form] = answers
		context['results'] = results
		return context

def consolidated(request, username):
	template_name = "feedback/report.html"
	user = get_user_model().objects.get(username=username)
	user_type = user.get_user_type()
	forms = FeedbackForm.objects.filter(recipient=user_type, active=True)
	results = dict()
	for form in forms:
		answers = Answer.objects.filter(form=form, recipient=user)
		results[form] = answers
	excellent = 0
	good = 0
	satisfactory = 0
	poor = 0
	very_poor = 0
	for form, answers in results.items():
		for que in form.question.all():
			for answer in answers:
				if answer.value == 'Excellent' and answer.question == que:
					excellent+=1
				if answer.value == 'Good' and answer.question == que:
					good+=1
				if answer.value == 'Satisfactory' and answer.question == que:
					satisfactory+=1
				if answer.value == 'Poor' and answer.question == que:
					poor+=1
				if answer.value == 'Very Poor' and answer.question == que:
					very_poor+=1
		# print(excellent)
		# print(good)
		# print(satisfactory)
		# print(poor)
		# print(very_poor)
		# print(form.title)
		total = (((excellent * 5) + (good * 4) + (satisfactory * 3) + (poor * 2) + (very_poor))/((excellent+good+satisfactory+poor+very_poor)*5)*100)
		# print(total)
		if not ConsolidatedReport.objects.filter(name = user.first_name, form_name = form.title, total = round(total, 2), department=user.department).exists():
			total_count = ConsolidatedReport.objects.create(name = user.first_name, form_name = form.title, total = round(total, 2), department=user.department)

	context = {"results" : results, "user" : user}
	return render(request, template_name, context)

def view_consolidated(request):
	template_name = "consolidated_report.html"
	report = ConsolidatedReport.objects.all()
	context = {"report": report}
	return render(request, template_name, context)

def sconsolidated(request, username):
	template_name = "feedback/student_report.html"
	user = get_user_model().objects.get(username=username)
	loggedin_user = request.user
	print(loggedin_user)
	user_type = loggedin_user.get_user_type()
	department = loggedin_user.department
	if user_type[0].name == 'AnonymousUser':
		return HttpResponseRedirect(reverse_lazy('login'))
	if username != loggedin_user.username and user_type[0].name == 'Faculty':
		return HttpResponseRedirect(reverse_lazy('dashboard'))
	if department.name != user.department.name and user_type[0].name != 'Principal':
		return HttpResponseRedirect(reverse_lazy('dashboard'))
	print('Generating Report')
	# print("|________________________|user|________________________|")
	# print(user)
	forms = FeedbackForm.objects.filter(user_type=5, active=True)
	data = Teaches.objects.filter(teacher__username=user)
	results = dict()

	for form in forms:
		answers = StudentAnswer.objects.filter(form=form, teacher__teacher__username=user)
		results[form] = answers

	# for i in data:
	# 	print(i.subject)
	good_total = 0
	value = list()
	for i in data:
		# print("________________________| CLASS: |________________________")
		# print("Subject",i.subject.name)
		# print("Section",i.sec)
		# print("Sem",i.sem.sem)
		ls = [i.sem.sem,i.sec,i.subject.name,i.ug,i.batch,i.sub_batch,i.department,i.subject.elective]
		for form, answers in results.items():
			excellent_total = 0
			good_total = 0
			satisfactory_total = 0
			poor_total = 0
			very_poor_total = 0
			l = list()
			que_count = 0
			for que in form.question.all():
				# print("________________________| QUESTION: |________________________")
				# print(que.text)
				que_count = 0
				excellent = 0
				good = 0
				satisfactory = 0
				poor = 0
				very_poor = 0
				for j in answers:
					# print("________________________| THEORY: |________________________")
					# print(i.subject.theory, j.teacher.subject.theory)
					# print("________________________| ELECTIVE: |________________________")
					# print(i.subject.elective, j.teacher.subject.elective)
					# print("________________________| PROJECT: |________________________")
					# print(i.subject.project, j.teacher.subject.project)
					res = bool()
					if que_count < i.count:
						if i == j.teacher:
							# print("________________________| RESULT: |________________________")
							res = True
							# print(res)
						if j.question == que:
							if j.value == 'Excellent':
								if res:
									excellent += 1
									excellent_total += 1
									que_count += 1

							if j.value == 'Good':
								if res:
									good += 1
									good_total += 1
									que_count += 1

							if j.value == 'Satisfactory':
								if res:
									satisfactory += 1
									satisfactory_total += 1
									que_count += 1

							if j.value == 'Poor':
								if res:
									poor += 1
									poor_total += 1
									que_count += 1

							if j.value == 'Very Poor':
								if res:
									very_poor += 1
									very_poor_total += 1
									que_count += 1

				if excellent or good or satisfactory or poor or very_poor:
					total = (((excellent * 5) + (good * 4) + (satisfactory * 3) + (poor * 2) + (very_poor))/((excellent+good+satisfactory+poor+very_poor)*5)*100)
					l.append([que.text, excellent, good, satisfactory, poor, very_poor, total])
					# print("________________________| List: |________________________")
					# for x in l:
					# 	print(x)
			if l:
				grand_total = (((excellent_total * 5) + (good_total * 4) + (satisfactory_total * 3) + (poor_total * 2) + (very_poor_total))/((excellent_total+good_total+satisfactory_total+poor_total+very_poor_total)*5)*100)
				ls.append(l)
				ls.append(["Total", excellent_total, good_total, satisfactory_total, poor_total, very_poor_total, grand_total])
			# print("________________________| LS: |________________________")
			# for x in ls:
			# 	print(x)
		value.append(ls)

		#

	# print("________________________| VALUE: |________________________")
	# for x in value:
	# 	print(x)

	context = {"user" : user, "report" : value,}
	return render(request, template_name, context)

@login_required(login_url='/signin/')
def student_view_consolidated(request):
	if not request.user.is_principal():
		return HttpResponseRedirect(reverse_lazy('dashboard'))
	template_name = "student_consolidated_report.html"
	report = StudentConsolidatedReport.objects.all().order_by('name')
	department = {'CSE': 'Computer Science & Engineering', 'MECH': 'Mechanical Engineering', 'CHEM': 'Chemistry', 'PHY': 'Phyiscs', 'MCA': 'MCA', 'MECH': 'Mechanical Engineering', 'TCE': 'Telecom Engineering' , 'EEE': 'Electrical Engineering', 'ECE': 'Electronics Engineering', 'CIVIL': 'Civil Engineering', 'ISE': 'Information Science Engineering', 'MATH' : 'Mathematics'}
	context = {"report": report, "dept": department}
	# for i in report:
	# 	print(i.name)
	# 	print(i.department)
	# 	print(i.total)
	return render(request, template_name, context)

@login_required(login_url='/signin/')
def student_view_consolidated_sixty(request):
	if not request.user.is_principal():
		return HttpResponseRedirect(reverse_lazy('dashboard'))
	template_name = "student_consolidated_report_sixty.html"
	report = StudentConsolidatedReport.objects.filter(total__lt = 60.0).order_by('name')
	context = {"report": report}
	# for i in report:
	# 	print(i.name)
	# 	print(i.department)
	# 	print(i.total)
	return render(request, template_name, context)

class Student_Report(TemplateView):
	template_name = "feedback/student_report.html"

	def get_context_data(self, username, *args, **kwargs):
		context = super(Student_Report, self).get_context_data(*args, **kwargs)
		user = get_user_model().objects.get(username=username)
		context['user'] = user
		# user_type = user.get_user_type()
		forms = FeedbackForm.objects.filter(user_type__name='Student', active=True)
		print(forms)
		results = dict()
		for form in forms:
			print(form)
			answers = StudentAnswer.objects.filter(form=form, teacher__teacher__username=user.username)
			results[form] = answers
		context['results'] = results
		return context

def Test_report(request, username):
	template_name = "feedback/student_report.html"
	user = get_user_model().objects.get(username=username)

	forms = FeedbackForm.objects.filter(user_type=5, active=True)
	data = Teaches.objects.filter(teacher__username=user)
	results = dict()

	for form in forms:
		answers = StudentAnswer.objects.filter(form=form, teacher__teacher__username=user)
		results[form] = answers

	# for i in data:
	# 	print(i.subject)

	value = list()
	for i in data:
		# print("________________________| CLASS: |________________________")
		# print("Subject",i.subject.name)
		# print("Section",i.sec)
		# print("Sem",i.sem.sem)
		ls = [i.sem.sem,i.sec,i.subject.name,i.ug,i.batch,i.sub_batch,i.department,i.subject.elective]
		for form, answers in results.items():
			excellent_total = 0
			good_total = 0
			satisfactory_total = 0
			poor_total = 0
			very_poor_total = 0
			l = list()
			que_count = 0
			for que in form.question.all():
				# print("________________________| QUESTION: |________________________")
				# print(que.text)
				que_count = 0
				excellent = 0
				good = 0
				satisfactory = 0
				poor = 0
				very_poor = 0
				for j in answers:
					# print("________________________| THEORY: |________________________")
					# print(i.subject.theory, j.teacher.subject.theory)
					# print("________________________| ELECTIVE: |________________________")
					# print(i.subject.elective, j.teacher.subject.elective)
					# print("________________________| PROJECT: |________________________")
					# print(i.subject.project, j.teacher.subject.project)
					res = bool()
					if que_count < i.count:
						if i == j.teacher:
							# print("________________________| RESULT: |________________________")
							res = True
							# print(res)
						if j.question == que:
							if j.value == 'Excellent':
								if res:
									excellent += 1
									excellent_total += 1
									que_count += 1

							if j.value == 'Good':
								if res:
									good += 1
									good_total += 1
									que_count += 1

							if j.value == 'Satisfactory':
								if res:
									satisfactory += 1
									satisfactory_total += 1
									que_count += 1

							if j.value == 'Poor':
								if res:
									poor += 1
									poor_total += 1
									que_count += 1

							if j.value == 'Very Poor':
								if res:
									very_poor += 1
									very_poor_total += 1
									que_count += 1

				if excellent or good or satisfactory or poor or very_poor:
					total = (((excellent * 5) + (good * 4) + (satisfactory * 3) + (poor * 2) + (very_poor))/((excellent+good+satisfactory+poor+very_poor)*5)*100)
					l.append([que.text, excellent, good, satisfactory, poor, very_poor, total])
					# print("________________________| List: |________________________")
					# for x in l:
					# 	print(x)
			if l:
				grand_total = (((excellent_total * 5) + (good_total * 4) + (satisfactory_total * 3) + (poor_total * 2) + (very_poor_total))/((excellent_total+good_total+satisfactory_total+poor_total+very_poor_total)*5)*100)
				ls.append(l)
				ls.append(["Total", excellent_total, good_total, satisfactory_total, poor_total, very_poor_total, grand_total])
			# print("________________________| LS: |________________________")
			# for x in ls:
			# 	print(x)
		value.append(ls)

		if not StudentConsolidatedReport.objects.filter(name = user.first_name, total = round(grand_total, 2), department=user.department, teacher=i).exists():
				total_count = StudentConsolidatedReport.objects.create(name = user.first_name, total = round(grand_total, 2), department=user.department, teacher=i)

	# print("________________________| VALUE: |________________________")
	# for x in value:
	# 	print(x)


	context = {"user" : user, "report" : value,}
	return render(request, template_name, context)
# def feedback(request):
# 	'''
# 	Displays the main student feedback form
# 	'''
# 	user = request.user.profile
# 	sub_list = request.session['sub_code_list']
# 	show_sub_list = request.session['show_sub_list']
# 	name = request.session['name']
# 	faculty = request.session['faculty']
# 	faculty_id = request.session['faculty_id']
# 	request.session['curr'] = sub_list[-1]
# 	c = request.session['curr']
# 	fid = faculty_id[0]
# 	teacher = Teacher.objects.get(fid=fid)
# 	stud_class = request.session['student_class']
# 	question_count = FeedbackQuestion.objects.all().count()
# 	AnswerFormSet = modelformset_factory(FeedbackAnswer, form=FeedbackAnswerForm, extra=question_count)

# 	if request.method == 'POST':

# 		formset = AnswerFormSet(request.POST, queryset=FeedbackAnswer.objects.none())
# 		if formset.is_valid():
# 			if request.session['theory_count'] > 0:
# 				for form, que in zip(formset, FeedbackQuestion.objects.filter(que_type='T')):
# 					ans = form.cleaned_data.get('answer')
# 					answer = FeedbackAnswer(answer=ans, faculty=teacher, question=que,
# 						sem_sec=stud_class,
# 						sub=request.session['curr'],
# 						dno = user.dno,
# 						)
# 					answer.save()
# 			elif request.session['lab_count'] > 0:
# 				for form, que in zip(formset, FeedbackQuestion.objects.filter(que_type='L')):
# 					ans = form.cleaned_data.get('answer')
# 					answer = FeedbackAnswer(answer=ans, faculty=teacher, question=que, sem_sec=stud_class, sub=request.session['curr'])
# 					answer.dno = user.dno
# 					answer.lab_batch = user.lab_batch
# 					answer.lab_sub_code = user.lab_sub_code
# 					answer.save()
# 			request.session['sub_list'] = sub_list.pop()
# 			request.session['faculty'] = faculty[1:]
# 			request.session['faculty_id'] = faculty_id[1:]
# 			if not request.session['theory_count'] == 0:
# 				request.session['theory_count'] -= 1

# 			else :
# 				request.session['lab_count'] -= 1

# 		if request.session['theory_count'] > 0 or request.session['lab_count'] > 0 :
# 			return HttpResponseRedirect(reverse_lazy('feedback_entry'))
# 		else:
# 			user.done = 'True'
# 			user.save()
# 			return HttpResponseRedirect(reverse_lazy('logout'))

# 	else:

# 		formset = AnswerFormSet(queryset=FeedbackAnswer.objects.none())
# 		if request.session['theory_count'] > 0:
# 			form_zip = zip(formset, FeedbackQuestion.objects.filter(que_type='T'))
# 		elif request.session['lab_count'] > 0:
# 			form_zip = zip(formset, FeedbackQuestion.objects.filter(que_type='L'))
# 		return render(request, 'feedback_new.html', {'formset':formset, 'form_zip':form_zip, 'subs': sub_list, 'curr': c, 'menu': show_sub_list, 'name': name, 'fname': faculty, 'cl': stud_class,})


# def select_teacher(request):
# 	'''
# 	To populate the select teacher dropdown for faculty report view
# 	'''
# 	d = request.GET.get("depa")
# 	fac = Teacher.objects.filter(dno__dno=d).extra(select={'length':'Length(fid)'}).order_by('length', 'fid')
# 	context = {"subject": fac}
# 	template_name = "report_select.html"
# 	return render(request, template_name, context)


# def show_report(request):
# 	'''
# 	Final report show view redirection
# 	'''
# 	fac_id = request.GET.get("fac_id")
# 	return redirect('/report_show/' + fac_id + '/')


# class ReportView(FormView):
# 	'''
# 	First page of the faculty report view portal
# 	Lets the user select the department
# 	'''
# 	template_name = "report_home.html"

# 	def get(self, request, *args, **kwargs):
# 		request.session['dno'] = 0
# 		dep = Department.objects.all()
# 		context = {"dep" : dep}
# 		return render(request, self.template_name, context)

# 	def post(self, request, *args, **kwargs):
# 		# gets the value of department selected
# 		d = request.POST.get("depa")
# 		# keeps the selected department in session
# 		request.session['dno'] = d
# 		return render(request, self.template_name)


# class ReportShowView(FormView):
# 	template_name = "report_password.html"

# 	def email_otp(self, random_otp, faculty):
# 		"""
# 		Sends OTP to email
# 		"""
# 		email = EmailMessage(
# 					'Feedback OTP',
# 					'Dear ' + faculty.fname.title() + ',\n\n' +'Your OTP for viewing your feedback report is:' + random_otp + '\n\nThanks,\nBFS-BMSIT\n\nPowered by DevX Labs, BMSIT&M' ,
# 					'Feedback Support <feedback@bmsit.in>',
# 					[faculty.email],

# 					)
# 		email.send()

# 	def get(self, request, *args, **kwargs):
# 		fac = Teacher.objects.all()
# 		request.session['report_otp_valid'] = False
# 		otp = r''.join(random.choice('01234ABCD') for i in range(8))
# 		request.session['otp'] = otp
# 		faculty = Teacher.objects.get(fid=self.kwargs['fac_id_report'])
# 		fac_email = faculty.email
# 		context = {"faculty" : fac, "otp" : otp, "email" : fac_email}
# 		self.email_otp(otp, faculty)
# 		return render(request, self.template_name, context)

# 	def post(self, request, *args, **kwargs):
# 		otp = request.session['otp']
# 		if otp == request.POST.get('report_otp'):
# 			request.session['report_otp_valid'] = True
# 			request.session['is_hod'] = False
# 			request.session['faculty_id_report'] = self.kwargs['fac_id_report']
# 			return redirect(reverse_lazy('generate_report'))
# 		else:
# 			return HttpResponse("Incorrect otp")


# class GeneratedReportView(TemplateView):
# 	'''
# 	Generates the report for individual faculty members
# 	'''
# 	template_name = 'repeated_report.html'
# 	def dispatch(self, request, *args, **kwargs):
# 		if not request.session['is_hod']:
# 			if request.session['report_otp_valid']:
# 				request.session['report_otp_valid'] = False
# 				return super(GeneratedReportView, self).dispatch(request, *args, **kwargs)
# 			else:
# 				return redirect('/report')
# 		else:
# 			return super(GeneratedReportView, self).dispatch(request, *args, **kwargs)

# 	# Prints branch name in the report
# 	def get_branch(self,dno):
# 		if dno == 1:
# 			return 'Computer Science & Engineering'
# 		if dno == 2:
# 			return 'Information Science & Engineering'
# 		if dno == 3:
# 			return "Civil Engineering"
# 		if dno == 4:
# 			return "Electronics and Communication Engineering"
# 		if dno == 5:
# 			return "Electrical and Electronics Engineering"
# 		if dno == 6:
# 			return "Telecommunication Engineering"
# 		if dno == 7:
# 			return "Mechanical Engineering"
# 		if dno == 8:
# 			return "Master of Computer Application"
# 		if dno == 9:
# 			return "Phyiscs"
# 		if dno == 10:
# 			return "Chemistry"
# 		if dno == 11:
# 			return "Maths"

# 	def get(self, request, *args, **kwargs):
# 		fac_id = request.session['faculty_id_report']
# 		teacher_list = Teacher.objects.filter(fid=fac_id)
# 		sub_list = []

# 		# get all subjects
# 		for teacher in teacher_list:
# 			for sub in TheoryTeaches.objects.filter(fid=teacher):
# 				sub_list.append(sub)
# 			for sub in ElectiveTeaches.objects.filter(fid=teacher):
# 				sub_list.append(sub)
# 			for sub in LabTeaches.objects.filter(fid=teacher):
# 				sub_list.append(sub)
# 		final_list = []

# 		for sub1 in sub_list:
# 			try:
# 				if sub1.lab_batch:
# 					que_list = FeedbackQuestion.objects.filter(que_type="L")
# 					que_type = 'L'
# 			except:
# 				que_list = FeedbackQuestion.objects.filter(que_type="T")
# 				que_type = 'T'
# 			que_dict = []
# 			for que in que_list:
# 				que_dict.append([que.question, [0, 0, 0, 0, 0, 0], que.que_type])
# 			Excellent = 0
# 			Good = 0
# 			Satisfactory = 0
# 			Poor = 0
# 			Very_Poor = 0
# 			if str(type(sub1).__name__) == 'ElectiveTeaches':
# 				answers = FeedbackAnswer.objects.filter(faculty__fid=sub1.fid.fid,
# 					sub=sub1.sub_code.sub_name)
# 			elif str(type(sub1).__name__) == 'LabTeaches':
# 				answers = FeedbackAnswer.objects.filter(faculty__fid=sub1.fid.fid,
# 					sem_sec=sub1.section, lab_batch=sub1.lab_batch)
# 				if sub1.lab_sub_code is not None :
# 					answers = FeedbackAnswer.objects.filter(faculty__fid=sub1.fid.fid,
# 					sem_sec=sub1.section, lab_batch=sub1.lab_batch, lab_sub_code=sub1.lab_sub_code)
# 				else :
# 					answers = FeedbackAnswer.objects.filter(faculty__fid=sub1.fid.fid,
# 					sem_sec=sub1.section, lab_batch=sub1.lab_batch)
# 			else:
# 				answers = FeedbackAnswer.objects.filter(faculty__fid=sub1.fid.fid, sub=sub1.sub_code.sub_name,
# 					sem_sec=sub1.section)
# 			final_percentage_sum = 0
# 			for q in que_dict:
# 				f_list = []
# 				answer_count = 0
# 				i = 0
# 				for a in answers:
# 					i += 1
# 					if a.question.question == q[0] and a.question.que_type == q[2]:
# 						if answer_count < sub1.count:
# 							answer_count += 1
# 							if a.answer == 'Excellent':
# 								Excellent += 1
# 								q[1][0] += 1
# 							elif a.answer == 'Good':
# 								q[1][1] += 1
# 								Good += 1
# 							elif a.answer == 'Satisfactory':
# 								q[1][2] += 1
# 								Satisfactory += 1
# 							elif a.answer == 'Poor':
# 								q[1][3] += 1
# 								Poor += 1
# 							elif a.answer == 'Very Poor':
# 								q[1][4] += 1
# 								Very_Poor += 1
# 				try:
# 					q[1][5] = ((q[1][0]*5 + q[1][1]*4 + q[1][2]*3 + q[1][3]*2 + q[1][4]*1))*100 / (answer_count*5)
# 					final_percentage_sum += q[1][5]
# 				except:
# 					pass
# 			total_percent = 0
# 			try:
# 				# Calculate the total
# 				if que_type == 'T':
# 					total_percent = final_percentage_sum / 20
# 				if que_type == 'L':
# 					total_percent = final_percentage_sum / 10
# 			except:
# 				pass
# 			sub1.total = Decimal(total_percent)
# 			sub1.save()

# 			branch = self.get_branch(sub1.dno_teaches)
# 			try :
# 				f_list = [sub1.fid, que_dict, total_percent, sub1.sub_code.sub_name, sub1.section, Excellent,
# 							 Good, Satisfactory, Poor, Very_Poor, answer_count, branch, sub1.lab_batch, sub1.lab_sub_code]
# 				final_list.append(f_list)
# 			except:
# 				f_list = [sub1.fid, que_dict, total_percent, sub1.sub_code.sub_name, sub1.section, Excellent,
# 							 Good, Satisfactory, Poor, Very_Poor, answer_count, branch]
# 				final_list.append(f_list)

# 		context = self.get_context_data()
# 		context["fa_name"] = teacher_list[0].fname
# 		context['final_list'] = final_list
# 		return render(request, self.template_name, context)


# class HODReportView(FormView):
# 	'''
# 	First page for the HOD Portal
# 	'''
# 	template_name = "report_hod.html"

# 	def get(self, request, *args, **kwargs):
# 		request.session['dno'] = 0
# 		dep = Department.objects.all()
# 		d = request.session['dno']
# 		context = {"dep" : dep}
# 		return render(request, self.template_name, context)

# 	def post(self, request, *args, **kwargs):
# 		d = request.POST.get("depa")
# 		department = str(Department.objects.get(dno=d))
# 		return redirect(reverse_lazy('hod_password', kwargs={
# 				'depart_name':department,
# 				}))

# class hod_password_done(FormView):
# 	'''
# 	Sends and verifies OTP to and from HOD
# 	'''
# 	template_name = "report_password_hod.html"

# 	def email_otp(self, random_otp, department):
# 		"""
# 		Sends OTP to email
# 		"""

# 		email = EmailMessage(
# 					'Feedback OTP',
# 					'Dear ' + department.hod_name.title() + ',\n\n' +'Your OTP for viewing your feedback report is:' + random_otp + '\n\nThanks,\nBFS-BMSIT\n\nPowered by DevX Labs, BMSIT&M' ,
# 					'Feedback Support <feedback@bmsit.in>',
# 					[department.hod_email],
# 					)
# 		email.send()

# 	def get(self, request, *args, **kwargs):
# 		'''
# 		generates OTP
# 		'''
# 		request.session['report_otp_valid'] = False
# 		otp = r''.join(random.choice('01234ABCD') for i in range(8))
# 		request.session['otp'] = otp
# 		department = Department.objects.get(dname=self.kwargs['depart_name'])
# 		request.session['depa'] = self.kwargs['depart_name']
# 		fac_email = department.hod_email
# 		context = {"otp" : otp, "email" : fac_email}
# 		self.email_otp(otp, department)
# 		return render(request, self.template_name, context)

# 	def post(self, request, *args, **kwargs):
# 		'''
# 		validates OTP
# 		'''
# 		otp = request.session['otp']
# 		if otp == request.POST.get('report_otp'):
# 			request.session['is_hod'] = True
# 			request.session['report_otp_valid'] = False
# 			return redirect(reverse_lazy('select_teacher_name_hod'))
# 		else:
# 			return HttpResponse("Incorrect OTP")


class select_teacher_hod(FormView):
	'''
	After authenticated by HOD OTP, lets HOD select individual faculty
	'''
	template_name = "report_select_hod.html"

	def get(self, request, *args, **kwargs):
		'''
		Populates the select faculty dropdown
		'''
		user = self.request.user
		username = user.username
		user_type = user.get_user_type()
		print(user_type[0])
		if str(user_type[0]).upper() == 'HOD':
			department = user.department
			faculty_list = User.objects.filter(department__name=department, user_type__name='Faculty').exclude(user_type__name='Student').order_by('first_name')
			#Teacher.objects.order_by('fname').filter(dno__dname=dname)
			context = {"faculty_list": faculty_list}
			return render(request, self.template_name, context)

		context = {"error": 'You are not authorized to view this page.'}
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		'''
		Geneartes the individual faculty report
		'''
		faculty_username = request.POST.get('faculty_username')
		return redirect(reverse_lazy('sconsolidated',kwargs={'username': faculty_username},))

class select_teacher_principal(FormView):
	'''
	After authenticated by HOD OTP, lets HOD select individual faculty
	'''
	template_name = "report_select_hod.html"

	def get(self, request, *args, **kwargs):
		'''
		Populates the select faculty dropdown
		'''
		user = self.request.user
		username = user.username
		user_type = user.get_user_type()
		print(user_type[0])
		if str(user_type[0]) == 'Principal':
			faculty_list = User.objects.filter(user_type__name='Faculty').exclude(user_type__name='Student').order_by('first_name')
			#Teacher.objects.order_by('fname').filter(dno__dname=dname)
			context = {"faculty_list": faculty_list}
			return render(request, self.template_name, context)

		context = {"error": 'You are not authorized to view this page.'}
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		'''
		Geneartes the individual faculty report
		'''
		faculty_username = request.POST.get('faculty_username')
		return redirect(reverse_lazy('sconsolidated',kwargs={'username': faculty_username},))

# class consolidated_principal(FormView):
# 	'''
# 	Portal for the HOD to view consolidated institute feedback
# 	'''
# 	template_name = "report_password_principal.html"

# 	def email_otp(self, random_otp):
# 		"""
# 		Sends OTP to email
# 		"""
# 		email = EmailMessage(
# 					'Feedback OTP',
# 					'Dear Sir' + ',\n\n' +'Your OTP for viewing your feedback report is:' + random_otp + '\n\nThanks,\nBFS-BMSIT\n\nPowered by DevX Labs, BMSIT&M' ,
# 					'Feedback Support <feedback@bmsit.in>',
# 					['principal@bmsit.in'],
# 					)
# 		email.send()

# 	def get(self, request, *args, **kwargs):
# 		'''
# 		generates and sends OTP to principal
# 		'''
# 		request.session['report_otp_valid'] = False
# 		otp = r''.join(random.choice('01234ABCD') for i in range(8))
# 		request.session['otp'] = otp
# 		fac_email = 'principal@bmsit.in'
# 		context = {"otp" : otp, "email" : fac_email}
# 		self.email_otp(otp)
# 		return render(request, self.template_name, context)

# 	def post(self, request, *args, **kwargs):
# 		'''
# 		validates principal OTP and if user is principal
# 		'''
# 		otp = request.session['otp']
# 		if otp == request.POST.get('report_otp'):
# 			request.session['is_principal'] = True
# 			request.session['report_otp_valid'] = False
# 			return redirect(reverse_lazy('consolidated_report'))
# 		else:
# 			return HttpResponse("Incorrect otp")


class consolidated_report(TemplateView):
	'''
	Consolidated report for viewing by principal
	'''
	template_name = "consolidated_report.html"
	def get(self, request, *args, **kwargs):

		if request.session['is_principal'] == True:
			teacher_list = Teacher.objects.all().order_by('dno__dno')
			sub_list = []
			for teacher in teacher_list:
				for sub in TheoryTeaches.objects.filter(fid=teacher):
					sub_list.append(sub)
				for sub in ElectiveTeaches.objects.filter(fid=teacher):
					sub_list.append(sub)
				for sub in LabTeaches.objects.filter(fid=teacher):
					sub_list.append(sub)
			context = self.get_context_data()
			context['subject_list'] = sub_list
			context['principal'] = True
			return render(request, self.template_name, context)
		else:
			return HttpResponse("Not Authorized, Please login")


# class consololidated_hod(TemplateView):
# 	'''
# 	Consolidated report for viewing by HOD
# 	'''
# 	template_name = "consolidated_report.html"
# 	def get(self, request, *args, **kwargs):

# 		if request.session['is_hod'] == True:
# 			depa = request.session['depa']
# 			teacher_list = Teacher.objects.filter(dno__dname=depa).order_by('dno__dno')
# 			sub_list = []
# 			# Get all teachers in the department
# 			for teacher in teacher_list:
# 				for sub in TheoryTeaches.objects.filter(fid=teacher):
# 					sub_list.append(sub)
# 				for sub in ElectiveTeaches.objects.filter(fid=teacher):
# 					sub_list.append(sub)
# 				for sub in LabTeaches.objects.filter(fid=teacher):
# 					sub_list.append(sub)
# 			context = self.get_context_data()
# 			context['subject_list'] = sub_list
# 			return render(request, self.template_name, context)
# 		else:
# 			return HttpResponse("Not Authorized, Only accessible by HOD")


# class less_than_60_hod(TemplateView):
# 	'''
# 	fetches all faculty of department with feedback less than 60, for HOD
# 	'''
# 	template_name = "consolidated_report.html"
# 	def get(self, request, *args, **kwargs):
# 		if request.session['is_hod'] == True:
# 			depa = request.session['depa']
# 			teacher_list = Teacher.objects.filter(dno__dname=depa).order_by('dno__dno')
# 			sub_list = []
# 			for teacher in teacher_list:
# 				for sub in TheoryTeaches.objects.filter(fid=teacher, total__lt=60):
# 					sub_list.append(sub)
# 				for sub in ElectiveTeaches.objects.filter(fid=teacher, total__lt=60):
# 					sub_list.append(sub)
# 				for sub in LabTeaches.objects.filter(fid=teacher, total__lt=60):
# 					sub_list.append(sub)
# 			context = self.get_context_data()
# 			context['subject_list'] = sub_list
# 			return render(request, self.template_name, context)
# 		else:
# 			return HttpResponse("Not Authorized, Only accessible by HOD")


# class less_than_60_principal(TemplateView):
# 	'''
# 	fetches all faculty with feedback less than 60, for viewing by principal
# 	'''
# 	template_name = "consolidated_report.html"
# 	def get(self, request, *args, **kwargs):
# 		if request.session['is_principal'] == True:
# 			teacher_list = Teacher.objects.all()
# 			sub_list = []
# 			for teacher in teacher_list:
# 				for sub in TheoryTeaches.objects.filter(fid=teacher, total__lt=60):
# 					sub_list.append(sub)
# 				for sub in ElectiveTeaches.objects.filter(fid=teacher, total__lt=60):
# 					sub_list.append(sub)
# 				for sub in LabTeaches.objects.filter(fid=teacher, total__lt=60):
# 					sub_list.append(sub)
# 			context = self.get_context_data()
# 			context['subject_list'] = sub_list
# 			return render(request, self.template_name, context)
# 		else:
# 			return HttpResponse("Not Authorized, Only accessible by principal")



# class report_not_viewed(TemplateView):
# 	'''
# 	fetches all faculty who are yet to view their report
# 	'''
# 	template_name = "report_not_seen.html"
# 	def get(self, request, *args, **kwargs):
# 		teacher_list = Teacher.objects.all()

# 		# Holds the final list of faculty who have'nt seen their report
# 		sub_list = []

# 		cse_list = []
# 		ece_list = []
# 		ise_list = []
# 		eee_list = []
# 		civ_list = []
# 		tce_list = []
# 		mech_list = []
# 		mca_list = []
# 		phy_list = []
# 		chem_list = []
# 		math_list = []

# 		# Adds faculty to sub_list by checking if total is None
# 		for teacher in teacher_list:
# 				for sub in TheoryTeaches.objects.filter(fid=teacher, total__isnull=True):
# 					sub_list.append(sub)
# 				for sub in ElectiveTeaches.objects.filter(fid=teacher, total__isnull=True):
# 					sub_list.append(sub)
# 				for sub in LabTeaches.objects.filter(fid=teacher, total__isnull=True):
# 					sub_list.append(sub)

# 		# Adds the faculty to their respective department lists
# 		for i in sub_list:
# 			if i.dno.dname == 'CSE':
# 				cse_list.append(i.fid.fname)
# 			if i.dno.dname == 'ECE':
# 				ece_list.append(i.fid.fname)
# 			if i.dno.dname == 'ISE':
# 				ise_list.append(i.fid.fname)
# 			if i.dno.dname == 'EEE':
# 				eee_list.append(i.fid.fname)
# 			if i.dno.dname == 'TCE':
# 				tce_list.append(i.fid.fname)
# 			if i.dno.dname == 'CIV':
# 				civ_list.append(i.fid.fname)
# 			if i.dno.dname == 'MECH':
# 				mech_list.append(i.fid.fname)
# 			if i.dno.dname == 'MCA':
# 				mca_list.append(i.fid.fname)
# 			if i.dno.dname == 'PHY':
# 				phy_list.append(i.fid.fname)
# 			if i.dno.dname == 'CHEM':
# 				chem_list.append(i.fid.fname)
# 			if i.dno.dname == 'MATH':
# 				math_list.append(i.fid.fname)

# 		# Total count of no. of faculty not viewed
# 		count = len(list(set(cse_list))) + len(list(set(ece_list))) + len(list(set(ise_list)))
# 		count = count + len(list(set(eee_list))) + len(list(set(tce_list))) + len(list(set(civ_list)))
# 		count = count + len(list(set(mech_list))) + len(list(set(mca_list))) + len(list(set(phy_list)))
# 		count = count + len(list(set(chem_list))) + len(list(set(math_list)))

# 		context = self.get_context_data()
# 		context['cse_list'] = list(set(cse_list))
# 		context['ece_list'] = list(set(ece_list))
# 		context['ise_list'] = list(set(ise_list))
# 		context['eee_list'] = list(set(eee_list))
# 		context['tce_list'] = list(set(tce_list))
# 		context['civ_list'] = list(set(civ_list))
# 		context['mech_list'] = list(set(mech_list))
# 		context['mca_list'] = list(set(mca_list))
# 		context['phy_list'] = list(set(phy_list))
# 		context['chem_list'] = list(set(chem_list))
# 		context['math_list'] = list(set(math_list))
# 		context['percent'] = ((146 - count)/146)*100
# 		context['count'] = count
# 		return render(request, self.template_name, context)

# def beta_report(request, username):
# 	template_name = "feedback/student_report.html"
# 	user = get_user_model().objects.get(username=username)
#
# 	forms = FeedbackForm.objects.filter(user_type=5, active=True)
# 	data = Teaches.objects.filter(teacher__username=user)
# 	results = dict()
# 	value = 0
# 	excellent = 0
#
# 	for i in data:
# 		for form in forms:
# 			for que in form.question.all():
# 				excellent = StudentAnswer.objects.filter(form=form, teacher=i, value='Excellent', question=que).count()
# 				print(excellent)
#
# 	context = {"user" : user, "report" : value,}
# 	return render(request, template_name, context)

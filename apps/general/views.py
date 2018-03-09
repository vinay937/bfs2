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
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.core import serializers
from django.forms.models import model_to_dict

import json
import csv

from django.views import View
from django.views.generic import TemplateView, FormView
from django.core.urlresolvers import resolve
from django.contrib.auth import logout

from .models import User
from apps.feedback.models import FeedbackForm

from apps.feedback.forms import FeedbackAnswerForm

from django.contrib.auth.hashers import make_password, check_password
import random
import urllib.parse as ap
import urllib.request
from django.core.mail import send_mail, EmailMessage

from .models import *
from django.db.models import Avg

# Create your views here.

def handler404(request):
	response = render_to_response('404.html', {}, context_instance=RequestContext(request))
	response.status_code = 404
	return response

def handler500(request):
	response = render_to_response('503.html', {}, context_instance=RequestContext(request))
	response.status_code = 500
	return response

def handler500(request):
	response = render_to_response('500.html', {}, context_instance=RequestContext(request))
	response.status_code = 500
	return response



class HomeView(FormView):
	'''
	Generates OTP, checks if user exists and has an email address.
	'''
	template_name = 'index.html'

	def phone_otp(self, random_otp, phone, usn):
		'''
		Sends OTP to phone
		'''
		phone1 = phone
		message = 'Please login with the OTP:' + random_otp + ' for USN:  '+ usn
		params = { 'to' : phone1, 'message' : message }
		baseUrl = 'https://alerts.sinfini.com/api/v3/index.php?method=sms&api_key=A5e952e0b7bec625b9885a52c4499bb55&format=json&sender=BMSITM&' + ap.urlencode(params)
		urllib.request.urlopen(baseUrl).read(1000)

	def password_update(self, random_otp, usn):
		"""
		Hashes the new password according to the OTP
		"""
		hashed_pwd = make_password(random_otp)
		User.objects.filter(username=usn).update(password=hashed_pwd)
		print(hashed_pwd)

	def email_otp(self, random_otp, qs):
		"""
		Sends OTP to email
		"""
		email = EmailMessage(
					'Feedback OTP',
					'Hi,' + qs.first_name + '\n\n' +'Your OTP for feedback is:' + random_otp + '\n\nThanks,\nBFS-BMSIT' ,
					'Feedback Support <feedback@bmsit.in>',
					[qs.email,],
					)
		email.send()
		print('OR: ' + qs.password)

	def is_admin(self, user):
		if user.is_superuser:
			return HttpResponseRedirect("/login/usn=" + user.username)

	def feedback_over_view(self, request):
		template_name = 'feedback_over_final.html'
		return render(request, template_name)

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name)

	def post(self, request, *args, **kwargs):
		random_otp = r''.join(random.choice('01234ABCD') for i in range(8))
		try:
			otp_page = 'login.html'
			usn = request.POST.get("usn1")
			usn = usn.upper()
			otp_page = otp_page + '/usn/' + usn
			qs = get_user_model().objects.get(username=usn)
			#Checks if user is admin and redirects directly
			self.is_admin(qs) 

			# Checks if done=False
			if not qs.done :

				if qs:
					# Checks if both email and phone doesn't exist
					if not qs.email and not qs.phone:
						messages.error(request, "Contact details incomplete. Contact coordinator")
					
					# Checks if both email and phone exist
					elif qs.email and qs.phone:
						self.phone_otp(random_otp, qs.phone, usn)
						self.email_otp(random_otp, qs)
						self.password_update(random_otp, usn)
						messages.error(request, "OTP sent to "+qs.phone+" and "+qs.email)
						return HttpResponseRedirect("/login/usn=" + usn)

					# Checks if only phone exists    
					elif qs.phone and not qs.email:
						self.phone_otp(random_otp, qs.phone, usn)
						self.password_update(random_otp, usn)
						messages.error(request, "Email not found, OTP sent to "+qs.phone)
						return HttpResponseRedirect("/login/usn=" + usn)

					# Checks if only email exists    
					elif qs.email and not qs.phone:
						self.email_otp(random_otp, qs)
						self.password_update(random_otp, usn)
						messages.error(request, "Phone number not found, OTP sent to "+qs.email)
						return HttpResponseRedirect("/login/usn=" + usn)

			else:
				messages.error(request, "You have already given the feedback! Thank You.")

		except User.DoesNotExist:
			messages.error(request, "Invalid USN")
		return render(request, self.template_name)
		

def done_view(request):
	'''
	Gets the rating after completion of feedback and redirects to home page.
	'''
	# rating = request.GET.get("rating")
	# if str(rating) == 'None':
	# 	rating = 5
	# starts = Rating.objects.create(star=rating)
	return redirect('/')


def exit_view(request):
	'''
	Displays the rating page
	'''
	logout(request)
	template_name = 'exit.html'
	return render(request, template_name)


def get_rating_view(request):
	'''
	Displays the current average rating
	'''
	template_name = 'rating.html'
	rating = Rating.objects.aggregate(Avg('star'))
	rating = rating['star__avg']
	context = {"rating" : rating}
	return render(request, template_name, context)



class MainView(TemplateView):
	'''
	Checks for the type of user and renders the count and users of their mandatory
	forms. 
	All the other individual forms are generated subsequently

	Passing the following to the variabes to the session
	`faclties` - if the user is a faculty, a list of all the faculties of 
		same department except the the user is stored 
	`hods` - if the user is hod, a list all the hods from different departments
		 are stored
	`count` - it is the total no of forms that the user needs to give feedback for.
		ie, for a faculty no. of collegues + no of individual forms

	TODO:// 
		1 - Move this to general `views.py` . Doesn't belong here
		2 - Add student check
	'''
	template_name = ""
	user_type = None


	def _faculty_mandatory(self):
		"""
		This is a compulsory form for the faculty where they give the 
		feedack to he other faculties
		"""

		# if the hod is also a faculty, he should be removed form the `faculties` list
		hod = UserType.objects.get(name="Hod")

		faculties = get_user_model().objects.filter(department=self.user.department,
			user_type__in=self.user_types).exclude(pk=self.user.pk)

		recipient_list = []
		for i in faculties:
			recipient_list.append(i.pk)
		self.request.session['recipients'] = recipient_list

		#This is used in post and will be removed on by one
		self.request.session['post_recipients'] = recipient_list

		self.request.session['count'] = faculties.count()

		# remove the form as it is already counted
		self.forms = self.forms.exclude(code="FF")
		
		return

	def _hod_mandatory(self):
		"""
		Compulsory form for HOD where they give feedback to the department HODs
		"""
		faculty = UserType.objects.get(name="Faculty")
		hods = get_user_model().objects.filter(user_type__in=self.user_types).exclude(pk=self.user.pk)
		print(hods)
		recipient_list = []
		for i in hods:
			recipient_list.append(i.pk)
		self.request.session['recipients'] = recipient_list

		#This is used in post and will be removed on by one
		self.request.session['post_recipients'] = recipient_list

		self.request.session['count'] = hods.count()
		# print(hods)
		# remove the form as it is already counted
		self.forms = self.forms.exclude(code="HH")
		
		return

	def get_context_data(self, **kwargs):
		context = super(MainView, self).get_context_data(**kwargs)
		self.user = self.request.user
		self.user_types = self.user.user_type.all()
		self.request.session['count'] = 0
		

		# if the user is hod as well as faculty, faculties mandatory forms shouldn't 
		# be displayed
		if self.user.is_faculty() and not self.user.is_hod():
			self.forms = FeedbackForm.objects.filter(active=True, user_type__in=self.user_types)
			self._faculty_mandatory()

		elif self.user.is_hod():
			# faculty mandatory forms are not required, so removed them
			faculty = UserType.objects.get(name="Faculty")

			self.user_types = self.user_types.exclude(name="Faculty")
			self.forms = FeedbackForm.objects.filter(active=True, user_type__in=self.user_types)
			
			self._hod_mandatory()

		else:
			self.forms = FeedbackForm.objects.filter(active=True, user_type__in=self.user_types)

		for form in self.forms:
			self.request.session['count'] += 1

		form_list = list()
		for f in self.forms:
			form_list.append(f.pk)
		self.request.session['form'] = form_list

		# they are the remaining recipients of the iterable forms
		form_recipients = list()
		for f in self.forms:
			form_recipients.append(f.recipient.name)

		self.request.session['form_recipients'] = form_recipients

		return context

	def get(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		return HttpResponseRedirect('/entry')

	def serialize_obj(self, obj):
	    data = serializers.serialize('json', obj)
	    struct = json.loads(data)
	    data = json.dumps(struct[0])
	    return data


# @login_required(login_url='/signin/')
# def main_view(request):
# 	'''
# 	Takes the user's subjects, segragates them into theory, lab and elective
# 	Passes subject details and faculty details to feedback view
# 	'''
# 	user = request.user.profile

# 	# Taking total subject count - IF WORKS, TO BE REMOVED
# 	# total = Subject.objects.filter(semester=user.semester,
# 	#                     dno=user.dno).count()
	
# 	# Getting all the subjects instances
# 	if user.mtech:
# 		sub_obj = Subject.objects.filter(semester=user.semester,
# 						dno=user.dno, mtech=True)
# 	else:
# 		sub_obj = Subject.objects.filter(semester=user.semester,
# 						dno=user.dno, mtech=False)
	
# 	sub_list = []
# 	sub_list_name = []
	
# 	# Getting `sub_code` to get the `*teaches` model
# 	for i in sub_obj:
# 		sub_list.append(i.sub_code)

# 	faculty = [] 

# 	# Getting theory subjects
# 	for sub in sub_list:
# 		try:
# 			if user.mtech:
# 				f = TheoryTeaches.objects.get(sub_code=sub, section=user.section)
# 			else:
# 				f = TheoryTeaches.objects.get(sub_code=sub, section=user.section)
# 			faculty.append(f)
# 		except TheoryTeaches.DoesNotExist:
# 			pass

# 	# Semester from where elective subjects starts
# 	# This is essential, change if semester changes
# 	eletive_semester = 5

# 	# Max no of electives in a semester, should be chnaged if no chnages
# 	no_of_elective = 2

# 	# Fir m
	
# 	# Only accessed if student has electives
# 	if user.semester >= eletive_semester and not user.mtech and user.dno.dno is not 8:
# 		f = [] # Getting elecitves
# 		for sub in sub_list:
# 			try:
# 				f.append(ElectiveTeaches.objects.get(sub_code__sub_code=user.elective1_id, section=user.section))
# 				f.append(ElectiveTeaches.objects.get(sub_code__sub_code=user.elective2_id, section=user.section))

# 			except ElectiveTeaches.DoesNotExist:
# 				pass
# 		for i in range(0, no_of_elective):
# 			faculty.append(f[i])

# 	# this is for mca, should go in different function
# 	if user.dno.dno == 8 and user.semester == 3:
# 		f = []
# 		for sub in sub_list:

# 			try:
# 				f.append(ElectiveTeaches.objects.get(sub_code__sub_code=user.elective1_id, section=user.section))

# 			except ElectiveTeaches.DoesNotExist:
# 				pass
# 		for i in range(0, 1):
# 			faculty.append(f[i])

# 	# this is for mtech
# 	if user.mtech:
# 		f = []
# 		for sub in sub_list:

# 			try:
# 				f.append(ElectiveTeaches.objects.get(sub_code__sub_code=user.elective1_id, section=user.section))

# 			except ElectiveTeaches.DoesNotExist:
# 				pass
# 		for i in range(0, 1):
# 			faculty.append(f[i])

# 	# Getting lab subjects
# 	for sub in sub_list:
# 		# This is for 1st sem, lab_sub_code ka chutiyapa
# 		if user.semester == 1:
# 			f = LabTeaches.objects.filter(sub_code=sub, section=user.section,
# 				lab_batch=user.lab_batch, lab_sub_code=user.lab_sub_code)
# 		else:
# 			f = LabTeaches.objects.filter(sub_code=sub, section=user.section, lab_batch=user.lab_batch)
# 		for k in f:
# 			faculty.append(k)

# 	# getting faculty name from the subjects
# 	for i in faculty:
# 		sub_list_name.append(i.sub_code.sub_name)

# 	lab_count = 0
# 	theory_count = 0

# 	# Getting theory and lab count for the feedback page
# 	for fac in faculty:
# 		try :
# 			if fac.lab_batch:
# 				lab_count += 1
# 		except:
# 			theory_count += 1

# 	faculty_name = []
# 	faculty_id = []
	
# 	#getting faculty name
# 	for a in faculty:
# 		faculty_name.append(a.fid.fname)
# 	for a in faculty:
# 		faculty_id.append(a.fid.fid)

# 	sec = str(user.section)
# 	student_class = sec

# 	# should be added to context
# 	request.session['show_sub_list']    = sub_list_name
# 	sub_list_name.reverse()
# 	request.session['theory_count']     = theory_count
# 	request.session['lab_count']        = lab_count
# 	request.session['sub_code_list']    = sub_list_name
# 	request.session['name']             = request.user.first_name
# 	request.session['faculty']          = faculty_name
# 	request.session['faculty_id']       = faculty_id
# 	request.session['student_class']    = student_class

# 	user.login_done = 'True'
# 	user.save()
# 	return HttpResponseRedirect(reverse_lazy('feedback_entry'))


# def counter_view(request):
# 	'''
# 	Displays the total number of students who have given feedback
# 	'''
# 	total_done = 0
# 	count = UserProfile.objects.all()
# 	for i in count:
# 		if i.done == True:
# 			total_done += 1
# 	template_name = 'total.html'
# 	print(total_done)
# 	context = {"total" : total_done}
# 	return render(request, template_name, context)



# def done_cron(request, dept_name):
# 	'''
# 	Downloads the list of remaing students, department wise in a CSV file
# 	'''
# 	student_list = UserProfile.objects.filter(dno__dname=dept_name).order_by('user__username')
# 	response = HttpResponse(content_type='text/csv')

# 	response['Content-Disposition'] = 'attachment; filename=feedback_pending_' +dept_name +'.csv'
# 	writer = csv.writer(response)
# 	for student in student_list:
# 		if not student.done:
# 			writer.writerow([student.user.username, student.user.first_name])
# 			print(student.user.username)

# 	return response


# class Dashboard(TemplateView):
# 	'''
# 	Shows the dashboard values
# 	'''
# 	template_name = 'dashboard.html'
	
# 	def get_context_data(self, **kwargs):
# 		context = super(Dashboard, self).get_context_data(**kwargs)
# 		total_done = 0
# 		count = UserProfile.objects.all()
# 		total_count = UserProfile.objects.all().count()
# 		total_done = UserProfile.objects.filter(done=True).count()
# 		total_remaining = total_count - total_done
# 		context = {"total" : total_done, "total_remaining": total_remaining}
# 		news = News.objects.all().order_by('-pk')
# 		news = news[:5]
# 		context['news'] = news
# 		rating = Rating.objects.aggregate(Avg('star'))
# 		rating = rating['star__avg']
# 		context["rating"] = rating

# 		context['cse'] = UserProfile.objects.filter(done=False, dno_id=1).count()
# 		context['ise'] = UserProfile.objects.filter(done=False, dno_id=2).count()
# 		context['civil'] = UserProfile.objects.filter(done=False, dno_id=3).count()
# 		context['ece'] = UserProfile.objects.filter(done=False, dno_id=4).count()
# 		context['eee'] = UserProfile.objects.filter(done=False, dno_id=5).count()
# 		context['tce'] = UserProfile.objects.filter(done=False, dno_id=6).count()
# 		context['mech'] = UserProfile.objects.filter(done=False, dno_id=7).count()
# 		context['mca'] = UserProfile.objects.filter(done=False, dno_id=8).count()

# 		return context
from django.contrib.auth.forms import AuthenticationForm
from django import forms

class LoginForm(AuthenticationForm):
	'''
	Form for taking Username and password
	'''
	username = forms.CharField(label="usn", max_length=30,
							   widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'usn1', 'id': 'usn','placeholder': 'Enter USN'}))
	password = forms.CharField(label="Password", max_length=30,
							   widget=forms.PasswordInput(attrs={'class': 'form-control', 'name': 'otp', 'id': 'otp', 'placeholder': 'Enter OTP'}))


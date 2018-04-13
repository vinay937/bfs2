from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import *

@admin.register(User)
class UserAdmin(DjangoUserAdmin):

	fieldsets = (
		(None, {'fields': ('username', 'email', 'password')}),
		(('Personal info'), {'fields': ('first_name', 'last_name', 'phone', 'department', 'date_of_joining')}),
		(('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
									   'groups', 'user_permissions')}),
		(('Academic Details'), {'fields': ('sem', 'sec', 'elective', 'batch', 'sub_batch')}),
		(('Designation'), {'fields': ('user_type', 'ug')}),
		(('Important dates'), {'fields': ('last_login', 'date_joined')}),
		(('Completion'), {'fields': ('partially_done', 'done')})
	)
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('email', 'password1', 'password2'),
		}),
	)

	list_display = ('username', 'first_name', 'last_name', 'phone', 'email')
	search_fields = ('email', 'first_name', 'last_name', 'username', 'phone')
	ordering = ('username',)

@admin.register(Teaches)
class TeachesAdmin(admin.ModelAdmin):
	list_display = ('teacher_first_name','subject_name','sem_sem','sec', 'department_name', 'batch', 'ug')
	search_fields = ('teacher__first_name', 'subject__name', 'subject__code')

	def teacher_first_name(self, instance):
		return instance.teacher.first_name

	def subject_name(self, instance):
		return instance.subject.name

	def department_name(self, instance):
		return instance.department.name

	def sem_sem(self, instance):
		return instance.sem.sem

admin.site.register(Subject)
admin.site.register(Department)
admin.site.register(Semester)
admin.site.register(UserType)

from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, Subject, Department, Teaches

@admin.register(User)
class UserAdmin(DjangoUserAdmin):

	fieldsets = (
		(None, {'fields': ('email', 'password')}),
		(('Personal info'), {'fields': ('first_name', 'last_name', 'phone', 'department', 'date_of_joining')}),
		(('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
									   'groups', 'user_permissions')}),
		(('Academic Details'), {'fields': ('sem', 'sec', 'elective', 'batch', 'sub_batch')}),
		(('Designation'), {'fields': ('faculty', 'hod', 'vice_principal', 'principal', 'institution')}),
		(('Important dates'), {'fields': ('last_login', 'date_joined')}),
		(('Completion'), {'fields': ('partially_done', 'done')})
	)
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('email', 'password1', 'password2'),
		}),
	)

	list_display = ('username', 'first_name', 'last_name','faculty', 'hod', 'vice_principal', 'principal', 'institution')
	search_fields = ('email', 'first_name', 'last_name')
	ordering = ('username',)

admin.site.register(Subject)
admin.site.register(Department)
admin.site.register(Teaches)
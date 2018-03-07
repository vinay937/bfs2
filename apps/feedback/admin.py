from django.contrib import admin

from .models import *

admin.site.register(FeedbackForm)
admin.site.register(Question)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):

	fieldsets = (
		(None, {'fields': ('question', 'teacher', 'form', 'recipient')}),
	)

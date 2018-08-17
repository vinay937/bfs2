from django.contrib import admin

from .models import *

admin.site.register(FeedbackForm)
admin.site.register(Question)
admin.site.register(ConsolidatedReport)
admin.site.register(StudentConsolidatedReport)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):

    fieldsets = ((None, {"fields": ("question", "teacher", "form", "recipient")}),)


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):

    fieldsets = ((None, {"fields": ("question", "teacher", "form", "recipient")}),)
    search_fields = ("teacher__teacher__first_name",)
    list_display = ["teacher", "get_code"]

    def get_code(self, obj):
        return obj.form.code

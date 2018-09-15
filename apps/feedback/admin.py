from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources

from .models import *

admin.site.register(FeedbackForm)
admin.site.register(Question)
admin.site.register(ConsolidatedReport)


class StudentConsolidatedResource(resources.ModelResource):
    class Meta:
        model = StudentConsolidatedReport


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


@admin.register(StudentConsolidatedReport)
class StudentConsolidatedAdmin(ImportExportModelAdmin):
    resource_class = StudentConsolidatedResource

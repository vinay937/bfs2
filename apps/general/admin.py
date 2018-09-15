from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import *

from import_export.admin import ImportExportModelAdmin
from import_export import resources

admin.site.site_header = "BMSIT Feedback System Admin Interface"


class UserResource(resources.ModelResource):
    class Meta:
        model = User


class TeachesResource(resources.ModelResource):
    class Meta:
        model = Teaches


class SubjectResource(resources.ModelResource):
    class Meta:
        model = Subject


@admin.register(User)
class UserAdmin(DjangoUserAdmin, ImportExportModelAdmin):

    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        (
            ("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone",
                    "department",
                    "date_of_joining",
                )
            },
        ),
        (
            ("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            ("Academic Details"),
            {"fields": ("sem", "sec", "elective", "batch", "sub_batch")},
        ),
        (("Designation"), {"fields": ("user_type", "ug")}),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
        (("Completion"), {"fields": ("partially_done", "done")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )

    list_display = ("username", "first_name", "last_name", "phone", "email")
    search_fields = ("email", "first_name", "last_name", "username", "phone")
    ordering = ("username",)

    resource_class = UserResource


@admin.register(Teaches)
class TeachesAdmin(ImportExportModelAdmin):
    list_display = (
        "teachers_first_name",
        "subject_name",
        "semester",
        "sec",
        "department_name",
        "batch",
        "ug",
    )
    search_fields = ("teacher__first_name", "subject__name", "subject__code")

    resource_class = TeachesResource

    def teachers_first_name(self, instance):
        return instance.teacher.first_name

    def subject_name(self, instance):
        return instance.subject.name

    def department_name(self, instance):
        return instance.department.name

    def semester(self, instance):
        return instance.sem.sem


@admin.register(Subject)
class TeachesAdmin(ImportExportModelAdmin):
    list_display = ("name", "code", "theory", "elective", "project")

    search_fields = ("name", "code")

    resource_class = SubjectResource


admin.site.register(Department)
admin.site.register(Semester)
admin.site.register(UserType)
admin.site.register(Message)

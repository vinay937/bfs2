from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^entry/', views.FeedbackView.as_view(), name='feedback_form'),
    url(r'^report/', views.Report.as_view(), name='report'),
    # url(r'^__/__/--/__/__reports/(?P<username>[-\w]+)/$',views.consolidated, name='reports-url'),
    url(r'^reportstudent/(?P<username>[-\w]+)/$',views.Student_Report.as_view(), name='reportstudent'),
    url(r'^sreports/(?P<username>[-\w.]+)/$',views.sconsolidated, name='sconsolidated'),
    url(r'^report-select-hod/$',views.select_teacher_hod.as_view(), name='hod-select-faculty'),
    url(r'^consolidated/$',views.student_view_consolidated, name='consolidated'),
    url(r'^consolidated_sixty/$',views.student_view_consolidated_sixty, name='consolidated_sixty'),
    url(r'^report-principal/$',views.select_teacher_principal.as_view(), name='principal-select-faculty'),
    # url(r'^__/__/--/__/__sreports/(?P<username>[-\w.]+)/$',views.Test_report, name='sreports-url'),
]

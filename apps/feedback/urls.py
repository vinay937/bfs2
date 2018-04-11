from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^entry/', views.FeedbackView.as_view(), name='feedback_form'),
    url(r'^report/', views.Report.as_view(), name='report'),
    url(r'^__/__/--/__/__reports/(?P<username>[-\w]+)/$',views.consolidated, name='reports-url'),
    url(r'^reportstudent/(?P<username>[-\w]+)/$',views.Student_Report.as_view(), name='reportstudent'),
    url(r'^__/__/--/__/__sreports/(?P<username>[-\w]+)/$',views.sconsolidated, name='sreports-url'),
]

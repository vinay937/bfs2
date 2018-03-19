from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^entry/', views.FeedbackView.as_view(), name='feedback_form'),
    url(r'^report/', views.Report.as_view(), name='report'),
    url(r'^__/__/--/__/__reports/(?P<username>[-\w]+)/$',views.report_scraper, name='reports-url'),
]

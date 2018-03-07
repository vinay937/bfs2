from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^entry/', views.FeedbackView.as_view(), name='feedback_form'),
    url(r'^report/', views.Report.as_view(), name='report'),
]

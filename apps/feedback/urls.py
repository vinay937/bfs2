from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^give/', views.MainView.as_view()),
]
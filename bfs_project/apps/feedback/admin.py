from django.contrib import admin

from .models import *

admin.site.register(FeedbackForm)
admin.site.register(Question)
admin.site.register(Answer)

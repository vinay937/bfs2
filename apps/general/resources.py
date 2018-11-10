from import_export import resources
from .models import User
from django.contrib.auth.models import User


class User1Resource(resources.ModelResource):
    class Meta:
        model = User
        #import_id_fields = ('username',)
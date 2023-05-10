from identity.models import UserAccount
from django.contrib.auth.forms import UsernameField
from django.forms.models import ModelForm

class UserChangeForm(ModelForm):
    class Meta:
        model = UserAccount
        fields = {'username', 'first_name', 'last_name', 'email', 'telephone', 'is_face_recognition_enabled'}
        field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_permissions = self.fields.get('user_permissions')
        if user_permissions:
            user_permissions.queryset = user_permissions.queryset.select_related('content_type')
            



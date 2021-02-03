from django import forms
from django.forms import ModelForm, Textarea
from django.core.exceptions import ValidationError

from django.contrib.auth import get_user_model
User = get_user_model()

class UserForm(ModelForm):
    first_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(max_length=254, required=True)

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        for field in self.fields:
            print(self.fields[field].widget)
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'gender', 'dob',  'bio',]
        widgets = {
            'bio': Textarea(attrs={'rows': 3}),
        }
        labels = {
            'first_name': 'First Name',
            'last_name' : 'Last Name',
            'dob' : 'Birth Date',
        }
        help_texts = {
            'email': 'Provide your work email',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError('A user with that email already exists.')
        return email

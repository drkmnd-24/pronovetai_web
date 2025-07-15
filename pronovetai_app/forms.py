from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import User, UserType


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password Confirmation', widget=forms.PasswordInput)

    user_type = forms.ModelChoiceField(
        queryset=UserType.objects.all(),
        required=True,
        label='User Type',
    )

    class Meta:
        model = User
        fields = ('username', 'email',
                  'first_name', 'last_name', 'user_type')

    def clean_password2(self):
        pw1 = self.cleaned_data.get('password1')
        pw2 = self.cleaned_data.get('password2')
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError('Password did not match')
        return pw2

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
            email=self.cleaned_data.get('email'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            user_type=self.cleaned_data['user_type'],
        )
        return user

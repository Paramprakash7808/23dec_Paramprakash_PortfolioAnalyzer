from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Profile

class UserLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if hasattr(user, 'profile') and user.profile.is_blocked:
            raise ValidationError(
                "This account has been blocked by an administrator.",
                code='blocked',
            )
        super().confirm_login_allowed(user)

class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['github_username', 'profile_image', 'bio']

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class RegisterForm(UserCreationForm):
    """
    Extends Django's built-in UserCreationForm to add an optional email field.
    UserCreationForm already handles:
      - Username validation (unique, allowed characters)
      - Password strength validation
      - Password confirmation matching
    """
    email = forms.EmailField(
        required=False,
        help_text='Optional. Used for account recovery in the future.'
    )

    class Meta:
        model = User
        # Fields rendered in this order in the template
        fields = ('username', 'email', 'password1', 'password2')

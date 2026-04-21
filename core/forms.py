from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Task


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


class TaskForm(forms.ModelForm):
    """
    Form for creating a new Task.
    The 'user' field is excluded — it is assigned automatically in the view
    from request.user to prevent users from assigning tasks to others.
    """
    class Meta:
        model = Task
        fields = ('title', 'description', 'due_time')
        widgets = {
            # DateTimeInput renders a datetime-local input for browser date picker
            'due_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tell Django to parse datetime-local format from the browser
        self.fields['due_time'].input_formats = ['%Y-%m-%dT%H:%M']

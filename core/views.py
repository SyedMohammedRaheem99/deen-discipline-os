from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm


@login_required
def home(request):
    """
    Homepage view — requires the user to be logged in.
    Unauthenticated users are redirected to /login/ (set via LOGIN_URL in settings).
    """
    return render(request, 'home.html')


def register(request):
    """
    Custom registration view.
    - GET:  Display the empty registration form.
    - POST: Validate, save the new user, log them in, redirect to homepage.
    Django's built-in login/logout views are handled by django.contrib.auth.urls.
    """
    # Redirect already-authenticated users away from the register page
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # save() creates the User record in the database
            user = form.save()
            # Log the user in immediately after registration (no need to re-enter credentials)
            login(request, user)
            return redirect('core:home')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})

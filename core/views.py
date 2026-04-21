from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, TaskForm
from .models import Task


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


# ===========================================================
# Task Views
# ===========================================================

@login_required
def task_list(request):
    """
    Display all tasks belonging to the logged-in user.
    Ordered by the model's default: newest first.
    """
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks/task_list.html', {'tasks': tasks})


@login_required
def task_create(request):
    """
    Create a new task for the logged-in user.
    - GET:  Show empty form.
    - POST: Validate, assign user, save, redirect to task list.
    """
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)   # Don't save to DB yet
            task.user = request.user          # Assign the logged-in user
            task.save()
            return redirect('core:task_list')
    else:
        form = TaskForm()

    return render(request, 'tasks/task_form.html', {'form': form})


@login_required
def task_toggle(request, task_id):
    """
    Toggle the completion status of a task (done ↔ pending).
    Only the task owner can toggle — get_object_or_404 with user filter
    ensures a user cannot toggle another user's task (returns 404 if not found).
    Accepts POST only to prevent accidental toggles via URL crawling.
    """
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, user=request.user)
        task.completed = not task.completed
        task.save()

    return redirect('core:task_list')

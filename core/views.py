from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import RegisterForm, TaskForm, JournalForm
from .models import Task, Prayer, Journal


@login_required
def home(request):
    """
    Dashboard — the main homepage showing today's performance summary.
    Computes tasks, prayers, journal, and discipline score for the logged-in user.
    """
    today = timezone.localdate()

    # ---- Tasks ----
    # All tasks created today by this user
    today_tasks = Task.objects.filter(user=request.user, created_at__date=today)
    total_tasks     = today_tasks.count()
    completed_tasks = today_tasks.filter(completed=True).count()
    pending_tasks   = total_tasks - completed_tasks

    # ---- Prayers ----
    # Auto-create today's prayer records if they don't exist yet
    # (same logic as prayer_list — keeps dashboard self-sufficient)
    for prayer_name in PRAYER_ORDER:
        Prayer.objects.get_or_create(
            user=request.user,
            date=today,
            prayer_name=prayer_name,
            defaults={'completed': False, 'on_time': False},
        )

    today_prayers    = Prayer.objects.filter(user=request.user, date=today)
    completed_prayers = today_prayers.filter(completed=True).count()
    ontime_prayers    = today_prayers.filter(on_time=True).count()

    # ---- Journal ----
    journal_entry = Journal.objects.filter(user=request.user, date=today).first()

    # ---- Discipline Score (out of 100) ----
    # Each completed prayer  → +10 points (max 50)
    # Each on-time prayer    → +5 bonus   (max 25)
    # Task completion ratio  → up to 25 points
    prayer_score  = completed_prayers * 10          # 0–50
    ontime_score  = ontime_prayers * 5              # 0–25

    # Task score: percentage of completed tasks, scaled to 25 points
    # If no tasks today, this portion is 0 (not penalised)
    if total_tasks > 0:
        task_score = int((completed_tasks / total_tasks) * 25)
    else:
        task_score = 0

    discipline_score = prayer_score + ontime_score + task_score  # 0–100

    return render(request, 'dashboard.html', {
        'today': today,
        # Tasks
        'total_tasks':     total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks':   pending_tasks,
        # Prayers
        'completed_prayers': completed_prayers,
        'ontime_prayers':    ontime_prayers,
        # Journal
        'journal_entry': journal_entry,
        # Score
        'discipline_score': discipline_score,
    })


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


# ===========================================================
# Prayer Views
# ===========================================================

# The canonical order of the 5 daily prayers
PRAYER_ORDER = ['fajr', 'dhuhr', 'asr', 'maghrib', 'isha']


@login_required
def prayer_list(request):
    """
    Show today's 5 prayers for the logged-in user.
    If any prayer record is missing for today, create it automatically.
    This ensures the user always sees all 5 prayers without manual setup.
    """
    today = timezone.localdate()  # Use localdate so it respects TIME_ZONE setting

    # Auto-create any missing prayer records for today using get_or_create.
    # This is idempotent — safe to call on every page load.
    for prayer_name in PRAYER_ORDER:
        Prayer.objects.get_or_create(
            user=request.user,
            date=today,
            prayer_name=prayer_name,
            # defaults only applied when creating (not when getting existing record)
            defaults={'completed': False, 'on_time': False},
        )

    # Fetch today's prayers and order them correctly (Fajr → Isha).
    # Alphabetical DB ordering would be wrong, so we sort by PRAYER_ORDER index.
    prayer_records = Prayer.objects.filter(user=request.user, date=today)
    prayer_map = {p.prayer_name: p for p in prayer_records}
    prayers = [prayer_map[name] for name in PRAYER_ORDER if name in prayer_map]

    return render(request, 'prayers/prayer_list.html', {
        'prayers': prayers,
        'today': today,
    })


@login_required
def prayer_toggle(request, prayer_id):
    """
    Toggle the completed status of a prayer (done ↔ missed).
    POST only. Filters by user to prevent cross-user tampering.
    If uncompleted, also resets on_time to False (can't be on-time if not done).
    """
    if request.method == 'POST':
        prayer = get_object_or_404(Prayer, id=prayer_id, user=request.user)
        prayer.completed = not prayer.completed

        # If marking as not completed, on_time can no longer be true
        if not prayer.completed:
            prayer.on_time = False

        prayer.save()

    return redirect('core:prayer_list')


@login_required
def prayer_on_time_toggle(request, prayer_id):
    """
    Toggle the on_time status of a prayer.
    POST only. Only allowed if the prayer is already marked completed.
    """
    if request.method == 'POST':
        prayer = get_object_or_404(Prayer, id=prayer_id, user=request.user)

        # Guard: on_time is only meaningful when the prayer is completed
        if prayer.completed:
            prayer.on_time = not prayer.on_time
            prayer.save()

    return redirect('core:prayer_list')


# ===========================================================
# Journal Views
# ===========================================================

@login_required
def journal_view(request):
    """
    Display today's journal entry for the logged-in user.
    - If an entry exists → pre-fill the form with existing content and rating.
    - If no entry yet → show a blank form.
    The save action is handled separately at /journal/save/.
    """
    today = timezone.localdate()

    # Try to fetch today's entry — None if it doesn't exist yet
    entry = Journal.objects.filter(user=request.user, date=today).first()

    # Pre-fill form with existing data if an entry exists, otherwise empty form
    form = JournalForm(instance=entry)

    return render(request, 'journal/journal.html', {
        'form': form,
        'entry': entry,   # Used in template to know if we're editing or creating
        'today': today,
    })


@login_required
def journal_save(request):
    """
    Create or update today's journal entry.
    POST only. Uses update_or_create to handle both cases cleanly:
    - First save of the day → creates a new Journal record.
    - Subsequent saves → updates the existing record.
    """
    if request.method != 'POST':
        return redirect('core:journal_view')

    today = timezone.localdate()
    form = JournalForm(request.POST)

    if form.is_valid():
        # update_or_create: find by (user, date), update with new values if found
        Journal.objects.update_or_create(
            user=request.user,
            date=today,
            defaults={
                'content': form.cleaned_data['content'],
                'rating':  form.cleaned_data['rating'],
            },
        )
        return redirect('core:journal_view')

    # If form is invalid, re-render with errors
    entry = Journal.objects.filter(user=request.user, date=today).first()
    return render(request, 'journal/journal.html', {
        'form': form,
        'entry': entry,
        'today': today,
    })

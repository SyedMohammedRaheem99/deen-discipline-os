import json
from datetime import datetime, timedelta

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Case, IntegerField, Q, Value, When
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import JournalForm, RegisterForm, TaskForm
from .models import FlowBlock, HealthLog, Journal, Prayer, Task


def _priority_order():
    return Case(
        When(priority='high',   then=Value(1)),
        When(priority='medium', then=Value(2)),
        When(priority='low',    then=Value(3)),
        default=Value(2),
        output_field=IntegerField(),
    )

PRAYER_ORDER = ['fajr', 'dhuhr', 'asr', 'maghrib', 'isha']


# ── Helpers ────────────────────────────────────────────────────────────────

def ensure_todays_prayers(user, today):
    for prayer_name in PRAYER_ORDER:
        Prayer.objects.get_or_create(
            user=user,
            date=today,
            prayer_name=prayer_name,
            defaults={'completed': False, 'on_time': False},
        )


def calculate_flow_analysis(user, today):
    blocks = FlowBlock.objects.filter(user=user, date=today)
    total     = blocks.count()
    completed = blocks.filter(is_completed=True).count()

    def pct(done, tot):
        return round((done / tot) * 100) if tot > 0 else 0

    work_total  = blocks.filter(block_type='work').count()
    work_done   = blocks.filter(block_type='work',   is_completed=True).count()
    health_total = blocks.filter(block_type='health').count()
    health_done  = blocks.filter(block_type='health', is_completed=True).count()
    dhikr_total  = blocks.filter(block_type='dhikr').count()
    dhikr_done   = blocks.filter(block_type='dhikr',  is_completed=True).count()

    work_pct   = pct(work_done,   work_total)
    health_pct = pct(health_done, health_total)
    dhikr_pct  = pct(dhikr_done,  dhikr_total)

    score = round((work_pct * 0.5) + (health_pct * 0.2) + (dhikr_pct * 0.3))

    if score >= 80:
        insight = "Strong discipline today. You're aligned."
    elif score >= 50:
        insight = "Good effort. Improve consistency."
    else:
        insight = "You lost structure today. Reset tomorrow."

    return {
        'flow_total':        total,
        'flow_completed':    completed,
        'flow_work_done':    work_done,
        'flow_work_total':   work_total,
        'flow_work_pct':     work_pct,
        'flow_health_done':  health_done,
        'flow_health_total': health_total,
        'flow_health_pct':   health_pct,
        'flow_dhikr_done':   dhikr_done,
        'flow_dhikr_total':  dhikr_total,
        'flow_dhikr_pct':    dhikr_pct,
        'flow_score':        score,
        'flow_insight':      insight,
    }


def calculate_discipline_score(completed_prayers, ontime_prayers, completed_tasks, total_tasks):
    prayer_score = completed_prayers * 10      # max 50
    ontime_score = ontime_prayers * 5          # max 25
    task_score = int((completed_tasks / total_tasks) * 25) if total_tasks > 0 else 0
    return prayer_score + ontime_score + task_score


def get_score_message(score):
    if score >= 80:
        return "You're aligned today. Keep going."
    elif score >= 50:
        return "You're on track. Stay consistent."
    return "Reset your focus. You can improve today."


def calculate_streak(user):
    today = timezone.localdate()
    streak = 0
    for days_back in range(1, 366):
        day = today - timedelta(days=days_back)
        prayers_done = Prayer.objects.filter(user=user, date=day, completed=True).count()
        tasks_done = Task.objects.filter(user=user, created_at__date=day, completed=True).count()
        if prayers_done >= 3 and tasks_done >= 1:
            streak += 1
        else:
            break

    today_prayers_done = Prayer.objects.filter(user=user, date=today, completed=True).count()
    today_tasks_done = Task.objects.filter(user=user, created_at__date=today, completed=True).count()
    if today_prayers_done >= 3 and today_tasks_done >= 1:
        streak += 1
    return streak


# ── Dashboard / Today ──────────────────────────────────────────────────────

@login_required
def home(request):
    today = timezone.localdate()

    # Prayers
    ensure_todays_prayers(request.user, today)
    prayer_records = Prayer.objects.filter(user=request.user, date=today)
    prayer_map = {p.prayer_name: p for p in prayer_records}
    today_prayers = [prayer_map[name] for name in PRAYER_ORDER if name in prayer_map]
    completed_prayers = sum(1 for p in today_prayers if p.completed)
    ontime_prayers = sum(1 for p in today_prayers if p.on_time)

    # Tasks — all pending tasks + today's completed tasks shown on dashboard
    display_tasks = Task.objects.filter(
        Q(user=request.user, completed=False) |
        Q(user=request.user, created_at__date=today, completed=True)
    ).distinct().order_by('completed', 'created_at')

    # Score uses only today's tasks
    score_tasks = Task.objects.filter(user=request.user, created_at__date=today)
    score_completed = score_tasks.filter(completed=True).count()
    score_total = score_tasks.count()

    completed_tasks_count = display_tasks.filter(completed=True).count()
    total_tasks_count = display_tasks.count()

    # Health
    health_log, _ = HealthLog.objects.get_or_create(user=request.user, date=today)

    # Journal
    journal_entry = Journal.objects.filter(user=request.user, date=today).first()

    # Score
    discipline_score = calculate_discipline_score(
        completed_prayers, ontime_prayers, score_completed, score_total
    )
    score_message = get_score_message(discipline_score)
    streak = calculate_streak(request.user)

    current_hour = datetime.now().hour
    is_morning = 5 <= current_hour < 13

    if current_hour < 12:
        greeting = "Good morning"
    elif current_hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    flow_analysis = calculate_flow_analysis(request.user, today)

    return render(request, 'dashboard.html', {
        'today': today,
        'today_prayers': today_prayers,
        'completed_prayers': completed_prayers,
        'ontime_prayers': ontime_prayers,
        'display_tasks': display_tasks,
        'completed_tasks_count': completed_tasks_count,
        'total_tasks_count': total_tasks_count,
        'health_log': health_log,
        'journal_entry': journal_entry,
        'discipline_score': discipline_score,
        'score_message': score_message,
        'streak': streak,
        'is_morning': is_morning,
        'greeting': greeting,
        **flow_analysis,
    })


# ── Auth ───────────────────────────────────────────────────────────────────

def register(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('core:home')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


# ── Tasks ──────────────────────────────────────────────────────────────────

@login_required
def task_list(request):
    today = timezone.localdate()
    pending = Task.objects.filter(user=request.user, completed=False).annotate(
        p_order=_priority_order()
    )

    # Today: no due date, OR due today, OR overdue
    today_tasks = pending.filter(
        Q(due_time__isnull=True) | Q(due_time__date__lte=today)
    ).order_by('p_order', 'created_at')

    # Upcoming: due strictly in the future
    upcoming_tasks = pending.filter(
        due_time__date__gt=today
    ).order_by('due_time', 'p_order')

    # Completed: most recent first, capped at 30
    completed_tasks = Task.objects.filter(
        user=request.user, completed=True
    ).order_by('-created_at')[:30]

    return render(request, 'tasks/task_list.html', {
        'today_tasks':     today_tasks,
        'upcoming_tasks':  upcoming_tasks,
        'completed_tasks': completed_tasks,
        'today':           today,
    })


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('core:task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})


@login_required
def task_toggle(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, user=request.user)
        task.completed = not task.completed
        task.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success':   True,
                'completed': task.completed,
                'task_id':   task.id,
                'title':     task.title,
                'priority':  task.priority,
                'due_time':  task.due_time.strftime('%b %d, %H:%M') if task.due_time else None,
                'toggle_url': reverse('core:task_toggle', args=[task.id]),
                'delete_url': reverse('core:task_delete', args=[task.id]),
            })

    return redirect('core:task_list')


@login_required
def task_delete(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, user=request.user)
        task.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
    return redirect('core:task_list')


@login_required
def task_quick_add(request):
    if request.method == 'POST':
        from django.utils.dateparse import parse_datetime

        try:
            data         = json.loads(request.body)
            title        = data.get('title', '').strip()
            priority     = data.get('priority', 'medium')
            due_time_str = data.get('due_time', '').strip()
        except (json.JSONDecodeError, AttributeError):
            title        = request.POST.get('title', '').strip()
            priority     = request.POST.get('priority', 'medium')
            due_time_str = request.POST.get('due_time', '').strip()

        if priority not in ('high', 'medium', 'low'):
            priority = 'medium'

        due_time = None
        if due_time_str:
            parsed = parse_datetime(due_time_str)
            if parsed:
                due_time = timezone.make_aware(parsed) if timezone.is_naive(parsed) else parsed

        if title:
            task = Task.objects.create(
                user=request.user,
                title=title,
                priority=priority,
                due_time=due_time,
            )
            return JsonResponse({
                'success':    True,
                'task_id':    task.id,
                'title':      task.title,
                'priority':   task.priority,
                'due_time':   task.due_time.strftime('%b %d · %H:%M') if task.due_time else None,
                'toggle_url': reverse('core:task_toggle', args=[task.id]),
                'delete_url': reverse('core:task_delete', args=[task.id]),
            })
        return JsonResponse({'success': False, 'error': 'Title required'}, status=400)
    return JsonResponse({'success': False}, status=405)


# ── Prayers ────────────────────────────────────────────────────────────────

@login_required
def prayer_list(request):
    today = timezone.localdate()
    ensure_todays_prayers(request.user, today)
    prayer_records = Prayer.objects.filter(user=request.user, date=today)
    prayer_map = {p.prayer_name: p for p in prayer_records}
    prayers = [prayer_map[name] for name in PRAYER_ORDER if name in prayer_map]
    return render(request, 'prayers/prayer_list.html', {'prayers': prayers, 'today': today})


@login_required
def prayer_toggle(request, prayer_id):
    if request.method == 'POST':
        prayer = get_object_or_404(Prayer, id=prayer_id, user=request.user)
        prayer.completed = not prayer.completed
        if not prayer.completed:
            prayer.on_time = False
        prayer.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            today = timezone.localdate()
            completed_count = Prayer.objects.filter(
                user=request.user, date=today, completed=True
            ).count()
            return JsonResponse({
                'success': True,
                'completed': prayer.completed,
                'on_time': prayer.on_time,
                'completed_count': completed_count,
            })

    return redirect('core:prayer_list')


@login_required
def prayer_on_time_toggle(request, prayer_id):
    if request.method == 'POST':
        prayer = get_object_or_404(Prayer, id=prayer_id, user=request.user)
        if prayer.completed:
            prayer.on_time = not prayer.on_time
            prayer.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'on_time': prayer.on_time})

    return redirect('core:prayer_list')


# ── Health ─────────────────────────────────────────────────────────────────

@login_required
def health_water_update(request):
    if request.method == 'POST':
        today = timezone.localdate()
        health_log, _ = HealthLog.objects.get_or_create(user=request.user, date=today)
        try:
            data = json.loads(request.body)
            action = data.get('action', 'increment')
        except (json.JSONDecodeError, AttributeError):
            action = request.POST.get('action', 'increment')

        if action == 'increment' and health_log.water_count < 20:
            health_log.water_count += 1
        elif action == 'decrement' and health_log.water_count > 0:
            health_log.water_count -= 1
        health_log.save()
        return JsonResponse({'success': True, 'count': health_log.water_count})
    return JsonResponse({'success': False}, status=405)


@login_required
def health_workout_toggle(request):
    if request.method == 'POST':
        today = timezone.localdate()
        health_log, _ = HealthLog.objects.get_or_create(user=request.user, date=today)
        health_log.workout_done = not health_log.workout_done
        health_log.save()
        return JsonResponse({'success': True, 'done': health_log.workout_done})
    return JsonResponse({'success': False}, status=405)


# ── Journal ────────────────────────────────────────────────────────────────

@login_required
def journal_view(request):
    today = timezone.localdate()
    entry = Journal.objects.filter(user=request.user, date=today).first()
    form = JournalForm(instance=entry)
    return render(request, 'journal/journal.html', {'form': form, 'entry': entry, 'today': today})


@login_required
def journal_save(request):
    if request.method != 'POST':
        return redirect('core:journal_view')

    today = timezone.localdate()
    form = JournalForm(request.POST)
    if form.is_valid():
        Journal.objects.update_or_create(
            user=request.user,
            date=today,
            defaults={
                'content': form.cleaned_data['content'],
                'rating': form.cleaned_data['rating'],
            },
        )
        return redirect('core:journal_view')

    entry = Journal.objects.filter(user=request.user, date=today).first()
    return render(request, 'journal/journal.html', {'form': form, 'entry': entry, 'today': today})


@login_required
def journal_delete(request):
    if request.method == 'POST':
        today = timezone.localdate()
        Journal.objects.filter(user=request.user, date=today).delete()
    return redirect('core:journal_view')


# ── Flow ────────────────────────────────────────────────────────────────────

_FLOW_CYCLE = [('work', 45), ('health', 10), ('dhikr', 5)]


def _generate_flow(user, date, start_h=6, start_m=0, end_h=22, end_m=0):
    from datetime import datetime as dt, timedelta
    FlowBlock.objects.filter(user=user, date=date).delete()
    blocks, current = [], dt(date.year, date.month, date.day, start_h, start_m)
    end_dt = dt(date.year, date.month, date.day, end_h, end_m)
    idx = 0
    while current < end_dt:
        btype, mins = _FLOW_CYCLE[idx % 3]
        bnd = current + timedelta(minutes=mins)
        if bnd > end_dt:
            break
        blocks.append(FlowBlock(user=user, date=date,
                                start_time=current.time(), end_time=bnd.time(),
                                block_type=btype))
        current, idx = bnd, idx + 1
    FlowBlock.objects.bulk_create(blocks)


@login_required
def flow_view(request):
    today = timezone.localdate()
    blocks = list(FlowBlock.objects.filter(user=request.user, date=today).order_by('start_time'))
    if not blocks:
        _generate_flow(request.user, today)
        blocks = list(FlowBlock.objects.filter(user=request.user, date=today).order_by('start_time'))

    now_time = datetime.now().time()
    current_block = next(
        (b for b in blocks if b.start_time <= now_time < b.end_time), None
    )

    # ID of the first block in the cycle that contains the current block
    current_cycle_first_id = None
    if current_block:
        idx = next((i for i, b in enumerate(blocks) if b.id == current_block.id), None)
        if idx is not None:
            current_cycle_first_id = blocks[(idx // 3) * 3].id

    # Default times shown in the regenerate form
    start_val = blocks[0].start_time.strftime('%H:%M') if blocks else '06:00'
    end_val   = blocks[-1].end_time.strftime('%H:%M')  if blocks else '22:00'

    return render(request, 'flow/flow.html', {
        'blocks':                 blocks,
        'current_block':          current_block,
        'current_cycle_first_id': current_cycle_first_id,
        'today':                  today,
        'start_val':              start_val,
        'end_val':                end_val,
    })


@login_required
def flow_generate(request):
    if request.method == 'POST':
        today = timezone.localdate()
        raw_start = request.POST.get('start_time', '06:00')
        raw_end   = request.POST.get('end_time',   '22:00')
        try:
            sh, sm = map(int, raw_start.split(':'))
            eh, em = map(int, raw_end.split(':'))
        except (ValueError, AttributeError):
            sh, sm, eh, em = 6, 0, 22, 0
        _generate_flow(request.user, today, sh, sm, eh, em)
    return redirect('core:flow')


@login_required
def flow_block_toggle(request, block_id):
    if request.method == 'POST':
        block = get_object_or_404(FlowBlock, id=block_id, user=request.user)
        block.is_completed = not block.is_completed
        block.save()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'completed': block.is_completed})
    return redirect('core:flow')

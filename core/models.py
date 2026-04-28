from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('high',   'High'),
        ('medium', 'Medium'),
        ('low',    'Low'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default='medium')
    due_time = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        status = 'Done' if self.completed else 'Pending'
        return f'{self.title} [{status}] — {self.user.username}'


class Prayer(models.Model):
    PRAYER_CHOICES = [
        ('fajr',    'Fajr'),
        ('dhuhr',   'Dhuhr'),
        ('asr',     'Asr'),
        ('maghrib', 'Maghrib'),
        ('isha',    'Isha'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prayers')
    date = models.DateField()
    prayer_name = models.CharField(max_length=10, choices=PRAYER_CHOICES)
    completed = models.BooleanField(default=False)
    on_time = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Prayer'
        verbose_name_plural = 'Prayers'
        unique_together = ['user', 'date', 'prayer_name']
        indexes = [
            models.Index(fields=['user', 'date']),
        ]

    def __str__(self):
        status = 'Done' if self.completed else 'Missed'
        return f'{self.get_prayer_name_display()} on {self.date} — {self.user.username} [{status}]'


class Journal(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 11)]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journals')
    date = models.DateField()
    content = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Journal'
        verbose_name_plural = 'Journals'
        unique_together = ['user', 'date']

    def __str__(self):
        return f'Journal {self.date} — {self.user.username} (Rating: {self.rating}/10)'


class HealthLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_logs')
    date = models.DateField()
    water_count = models.IntegerField(default=0)
    workout_done = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'date']
        verbose_name = 'Health Log'
        verbose_name_plural = 'Health Logs'

    def __str__(self):
        return f'Health {self.date} — {self.user.username}'


class FlowBlock(models.Model):
    BLOCK_TYPES = [
        ('work',   'Work'),
        ('health', 'Health'),
        ('dhikr',  'Dhikr'),
    ]

    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flow_blocks')
    date         = models.DateField()
    start_time   = models.TimeField()
    end_time     = models.TimeField()
    block_type   = models.CharField(max_length=6, choices=BLOCK_TYPES)
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['date', 'start_time']
        verbose_name = 'Flow Block'
        verbose_name_plural = 'Flow Blocks'

    def __str__(self):
        return f'{self.get_block_type_display()} {self.start_time}–{self.end_time} ({self.date})'

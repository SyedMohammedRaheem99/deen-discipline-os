from django.db import models
from django.contrib.auth.models import User


# ===========================================================
# Task Model
# Represents a single to-do item belonging to a user.
# ===========================================================

class Task(models.Model):
    # The user who owns this task. Deleting the user removes all their tasks.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')

    title = models.CharField(max_length=200)

    # Optional longer description — blank allowed in forms and DB
    description = models.TextField(blank=True)

    # Optional deadline — not every task needs one
    due_time = models.DateTimeField(null=True, blank=True)

    completed = models.BooleanField(default=False)

    # Set once on creation; never updated automatically
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Newest tasks appear first in querysets by default
        ordering = ['-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        status = 'Done' if self.completed else 'Pending'
        return f'{self.title} [{status}] — {self.user.username}'


# ===========================================================
# Prayer Model
# Tracks whether a user performed each of the 5 daily prayers.
# One record per prayer per day per user.
# ===========================================================

class Prayer(models.Model):

    # Choices for the 5 obligatory daily prayers, in order
    PRAYER_CHOICES = [
        ('fajr',    'Fajr'),
        ('dhuhr',   'Dhuhr'),
        ('asr',     'Asr'),
        ('maghrib', 'Maghrib'),
        ('isha',    'Isha'),
    ]

    # The user who owns this prayer record
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prayers')

    # The calendar date this record belongs to (not a datetime — one entry per day per prayer)
    date = models.DateField()

    prayer_name = models.CharField(max_length=10, choices=PRAYER_CHOICES)

    # Did the user perform this prayer at all?
    completed = models.BooleanField(default=False)

    # Was it performed within the correct prayer time window?
    on_time = models.BooleanField(default=False)

    class Meta:
        # Most recent dates first
        ordering = ['-date']
        verbose_name = 'Prayer'
        verbose_name_plural = 'Prayers'
        # Prevent duplicate entries: one record per user, per prayer, per day
        unique_together = ['user', 'date', 'prayer_name']
        # Composite index speeds up the most common query: "get all prayers for user X on date Y"
        # This runs on every dashboard load, so the index pays off as data grows
        indexes = [
            models.Index(fields=['user', 'date']),
        ]

    def __str__(self):
        status = 'Done' if self.completed else 'Missed'
        return f'{self.get_prayer_name_display()} on {self.date} — {self.user.username} [{status}]'


# ===========================================================
# Journal Model
# One journal entry per user per day — a daily reflection log.
# ===========================================================

class Journal(models.Model):

    # Rating choices from 1 to 10 — displayed as "1", "2", ..., "10"
    RATING_CHOICES = [(i, str(i)) for i in range(1, 11)]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journals')

    # One entry per calendar day — enforced by unique_together below
    date = models.DateField()

    # The body of the journal entry
    content = models.TextField()

    # How the user rates their day (1 = terrible, 10 = excellent)
    rating = models.IntegerField(choices=RATING_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Journal'
        verbose_name_plural = 'Journals'
        # Enforce one entry per user per day at the database level
        unique_together = ['user', 'date']

    def __str__(self):
        return f'Journal {self.date} — {self.user.username} (Rating: {self.rating}/10)'

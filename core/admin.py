from django.contrib import admin
from .models import Task, Prayer, Journal


# ===========================================================
# Task Admin
# ===========================================================

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):

    # Columns shown in the task list view
    list_display = ('title', 'user', 'completed', 'due_time', 'created_at')

    # Sidebar filters for quick narrowing
    list_filter = ('completed', 'created_at')

    # Search across title and description fields
    search_fields = ('title', 'description')

    # Newest tasks at the top (mirrors model Meta ordering)
    ordering = ('-created_at',)


# ===========================================================
# Prayer Admin
# ===========================================================

@admin.register(Prayer)
class PrayerAdmin(admin.ModelAdmin):

    # Columns shown in the prayer list view
    list_display = ('user', 'date', 'prayer_name', 'completed', 'on_time')

    # Sidebar filters — useful for checking specific prayers or dates
    list_filter = ('prayer_name', 'completed', 'on_time', 'date')

    # Search by the related user's username (double underscore = follow FK)
    search_fields = ('user__username',)

    # Most recent prayer entries at the top
    ordering = ('-date',)


# ===========================================================
# Journal Admin
# ===========================================================

@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):

    # Columns shown in the journal list view
    list_display = ('user', 'date', 'rating', 'created_at')

    # Filter by rating or date
    list_filter = ('rating', 'date')

    # Search by username
    search_fields = ('user__username',)

    # Most recent entries at the top
    ordering = ('-date',)

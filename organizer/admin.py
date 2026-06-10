from django.contrib import admin
from .models import Task, Project, Comment, Subtask

# admin.site.register(Task)
# admin.site.register(Project)

# Register your models here.
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Model zadania do wykonania"""
    list_display = ('title', 'project', 'done', 'order', 'create_date', 'end_date', 'user', 'priority')
    list_filter = ('done', 'project')
    search_fields = ('title', 'description')
    readonly_fields = ('order', 'id', 'create_date', 'end_date')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Model projektu"""
    pass

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Model komentarza do zadania"""
    list_display = ('task', 'text', 'created_at')
    search_fields = ('text',)
    readonly_fields = ('created_at',)

@admin.register(Subtask)
class SubtaskAdmin(admin.ModelAdmin):
    """Model podzadania związanego z zadaniem"""
    list_display = ('task', 'title', 'done')
    list_filter = ('done',)
    search_fields = ('title', 'description')

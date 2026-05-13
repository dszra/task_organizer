from django.contrib import admin
from .models import Task, Project

# admin.site.register(Task)
# admin.site.register(Project)

# Register your models here.
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Model zadania do wykonania"""
    list_display = ('title', 'project', 'done', 'order')
    list_filter = ('done', 'project')
    search_fields = ('title', 'description')
    readonly_fields = ('order', 'id', 'create_date', 'end_date')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Model projektu"""
    pass

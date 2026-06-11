from django.db import models
from django.utils import timezone


class Project(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Category(models.TextChoices):
    BUG = 'BUG', 'Bug'
    FEATURE = 'FEATURE', 'Feature'
    IMPROVEMENT = 'IMPROVEMENT', 'Improvement'
    TECH_TASK = 'TECH_TASK', 'Technical Task'
    REFRACTORING = 'REFACTORING', 'Refactoring'
    MAINTENANCE = 'MAINTENANCE', 'Maintenance'
    TESTING = 'TESTING', 'Testing'
    DOCUMENTATION = 'DOCUMENTATION', 'Documentation'

class Priority(models.TextChoices):
    LOW = 'LOW', 'Low'
    MEDIUM = 'MEDIUM', 'Medium'
    HIGH = 'HIGH', 'High'


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    own_end_date = models.DateField(null=True, blank=True)
    done = models.BooleanField(default=False)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True
    )
    order = models.PositiveIntegerField(db_index=True, null=True, blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=None, null=True, blank=True)
    priority = models.CharField(max_length=20, choices=Priority.choices, default="LOW")

    

    def order_num(self):
        if not self.pk and not self.done and self.order is None or self.order is 0:
            high_order = Task.objects.filter(done=False).aggregate(models.Max('order'))['order__max']
            print(f"High order for project '{self.project}': {high_order}")
            self.order = (high_order + 1) if high_order is not None else 1
        if self.done:
            self.order = 0
        return self.order
    
    def update_end_date(self):
        if self.done and not self.end_date:
            self.end_date = timezone.now()
        elif not self.done:
            self.end_date = None
    
    def save(self, *args, **kwargs):
        self.order = self.order_num()
        self.update_end = self.update_end_date()
        if not self.user:
            self.user = self.request.user
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order']

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment on {self.task.title} at {self.created_at}"
    
class Subtask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=300, help_text="Title of the subtask")
    description = models.TextField(null=True, blank=True)
    done = models.BooleanField(default=False)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
    
    def update_end_date(self):
        if self.done and not self.end_date:
            self.end_date = timezone.now()
        elif not self.done:
            self.end_date = None
    
    def save(self, *args, **kwargs):
        self.update_end_date()
        super().save(*args, **kwargs)
    


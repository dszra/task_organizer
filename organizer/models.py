from django.db import models
from django.utils import timezone


class Project(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    done = models.BooleanField(default=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True
    )
    order = models.PositiveIntegerField(db_index=True, null=True, blank=True)

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
        self.update = self.update_end_date()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order']
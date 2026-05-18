from .models import Task
from django import forms

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'project', 'done']
        widgets = {
            'done': forms.CheckboxInput(attrs={'class': 'task-done-checkbox'}),
        }

from .models import Task, Comment, Subtask
from django.shortcuts import render, redirect
from django import forms

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'project', 'done', 'category', 'own_end_date', 'priority']
        widgets = {
            'done': forms.CheckboxInput(attrs={'class': 'task-done-checkbox'}),
            'category': forms.Select(attrs={'class': 'task-category-select'}),
            'own_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'task-end-date-input'}),
            'project': forms.Select(attrs={'class': 'task-project-select', }),
            'priority': forms.Select(attrs={'class': 'task-priority-select'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'cols': 40, 'placeholder': 'Add a commentt...'}),
        }

class SubtaskForm(forms.ModelForm):
    class Meta:
        model = Subtask
        fields = ['title', 'description', 'done']
        widgets = {
            'done': forms.CheckboxInput(attrs={'class': 'subtask-done-checkbox'}),
        }

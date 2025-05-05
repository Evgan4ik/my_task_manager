from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'is_completed']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }
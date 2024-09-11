from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control border-0 bg-light px-4 py-3', 'rows': 9, 'placeholder': 'Input your Query or Feedback here...'}),
        }
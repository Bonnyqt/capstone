from django import forms
from .models import Feedback
from .models import UserProfile

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['email', 'feedback']  # Use 'feedback' instead of 'message'
        widgets = {
            'feedback': forms.Textarea(attrs={
                'class': 'form-control border-0 bg-light px-4 py-3',
                'rows': 9,
                'placeholder': 'Input your Query or Feedback here...'
            }),
        }



class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)

    class Meta:
        model = UserProfile
        fields = ['section', 'program']


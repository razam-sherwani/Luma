from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        widget=forms.RadioSelect,
        help_text="Select your role to get the appropriate dashboard experience."
    )
    specialty = forms.CharField(
        max_length=100,
        required=False,
        help_text="Required for Healthcare Providers (HCP). Your medical specialty or area of practice."
    )
    
    class Meta:
        model = User
        fields = ('username', 'role', 'specialty', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = "Enter your professional username."
        
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                role=self.cleaned_data['role'],
                specialty=self.cleaned_data.get('specialty', '')
            )
        return user
from django import forms
from .models import User, StudentProfile

class StudentSignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    roll_number = forms.CharField(max_length=20, required=True)
    batch_year = forms.CharField(max_length=10, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        # Save the basic user info first
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_student = True # Automatically assign the student role
        
        if commit:
            user.save()
            # Immediately create their linked profile
            StudentProfile.objects.create(
                user=user,
                roll_number=self.cleaned_data['roll_number'],
                batch_year=self.cleaned_data['batch_year']
            )
        return user
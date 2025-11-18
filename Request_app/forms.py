from django import forms
from django.contrib.auth.models import User
from .models import Profile, MaintenanceRequest

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(
        choices=[('', '--- choose role ---')] + list(Profile.ROLE_CHOICES),
        required=True,
        label='Role'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        help_texts = {
            'username': None,   # removes "Required. 150 characters..." text
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    

    
class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput,
        label='New Password'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        label='Confirm Password'
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['title', 'description', 'category']
        widgets = {
            'description': forms.Textarea(attrs={'rows':4}),
        }

    def clean_description(self):
        desc = self.cleaned_data.get('description', '').strip()
        if not desc:
            raise forms.ValidationError("Description is required.")
        return desc

    def clean_category(self):
        cat = self.cleaned_data.get('category')
        if not cat:
            raise forms.ValidationError("Category is required.")
        return cat


class AssignRequestForm(forms.Form):
    technician = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True), required=True, label="Assign to (Technician / Staff)")

    def __init__(self, *args, **kwargs):
        tech_qs = kwargs.pop('tech_qs', None)
        super().__init__(*args, **kwargs)
        if tech_qs is not None:
            self.fields['technician'].queryset = tech_qs


class ChangeStatusForm(forms.Form):
    status = forms.ChoiceField(choices=MaintenanceRequest.STATUS_CHOICES, required=True)
    resolution_notes = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), required=False)



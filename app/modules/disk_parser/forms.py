from django import forms
from .models import PublicKey

class PublicKeyForm(forms.ModelForm):
    class Meta:
        model = PublicKey
        fields = ['key']
        widgets = {
            'key': forms.Textarea(attrs={'cols': 80, 'rows': 4}),
        }
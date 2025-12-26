from django import forms
from .models import PortfolioItem

class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = ['title', 'category', 'description', 'cover_image', 'event_date']
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'}), # ใช้ปฏิทินเลือกวันที่
            'description': forms.Textarea(attrs={'rows': 4}),
        }
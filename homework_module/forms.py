from django.utils.translation import gettext_lazy as _
from .models import Homework, HomeworkResult
from django import forms


class HomeworkForm(forms.ModelForm):
    assigned_to = forms.MultipleChoiceField(
        required=True,
        widget=forms.SelectMultiple(attrs={
            "class": "form-control"
        })
    )

    class Meta:
        model = Homework
        fields = ("title", "description", "for_date", "difficulty")
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": "3",
            }),
            "for_date": forms.DateInput(attrs={
                "class": "form-control",
                "data-mask": "99/99/9999",
            }),
            "difficulty": forms.Select(attrs={
                "class": "form-control"
            }),
        }


class HomeworkResultForm(forms.ModelForm):
    student = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={
            "class": "form-select"
        })
    )
    homework = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={
            "class": "form-select"
        })
    )

    class Meta:
        model = HomeworkResult
        fields = ("result", "status")
        widgets = {
            "result": forms.FileInput(attrs={
                "class": "form-control",
                "type": "file"
            }),
            "status": forms.TextInput(attrs={"class": "form-select"}),
        }


    def __init__(self, *args, **kwargs):
        show_status = kwargs.pop("show_status", False)

        super().__init__(*args, **kwargs)

        if not show_status:
            self.fields.pop("status")

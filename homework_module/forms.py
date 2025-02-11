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
        fields = ("title", "description", "for_date")
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
        }


class HomeworkResultForm(forms.ModelForm):
    homework = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={
            "class": "form-control"
        })
    )

    # class Meta:
    #     model = HomeworkResult
    #     fields = ("result",)
    #     widgets = {"result": forms.FileInput(attrs={"class": "form-control"})}

    def __init__(self, *args, **kwargs):
        show_homework = kwargs.pop("show_homework", False)

        super().__init__(*args, **kwargs)

        if not show_homework:
            self.fields.pop("homework")

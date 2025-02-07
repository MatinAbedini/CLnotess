from django import forms
from .models import Exam, ExamResult

class ExamForm(forms.ModelForm):
    assigned_to = forms.MultipleChoiceField(
        required=True,
        widget=forms.SelectMultiple(attrs={
            "class": "form-control"
        })
    )

    class Meta:
        model = Exam
        fields = ("title", "description", "for_date", "duration", "difficulty")
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
            "duration": forms.TimeInput(attrs={
                "class": "form-control",
                "data-mask": "99/99",
            }),
            "difficulty": forms.Select(attrs={
                "class": "form-control"
            }),
        }

    def __init__(self, *args, **kwargs):
        show_difficulty = kwargs.pop("show_difficulty", False)

        super().__init__(*args, **kwargs)

        if not show_difficulty:
            self.fields.pop("difficulty")


class ExamResultForm(forms.ModelForm):
    student = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={
            "class": "form-select"
        })
    )
    exam = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={
            "class": "form-select"
        })
    )

    class Meta:
        model = ExamResult
        fields = ("correct_answers", "incorrect_answers")
        widgets = {
            "correct_answers": forms.TextInput(attrs={"class": "form-control"}),
            "incorrect_answers": forms.TextInput(attrs={"class": "form-control"}),
        }

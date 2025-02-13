from django import forms
from .models import Exam, ExamResult

class ExamForm(forms.ModelForm):
    assigned_to = forms.MultipleChoiceField(
        required=True,
        widget=forms.SelectMultiple(attrs={
            "class": "form-control",
            "dir": "rtl",
        })
    )

    class Meta:
        model = Exam
        fields = ("title", "description", "for_date", "duration", "difficulty", "questions")
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "dir": "rtl",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": "3",
                "dir": "rtl",
            }),
            "for_date": forms.TextInput(attrs={
                "class": "form-control",
                "data-mask": "9999-99-99",
                "data-plugin":"touchSpin",
            }),
            "duration": forms.NumberInput(attrs={
                "class": "form-control",
                "dir": "rtl",
            }),
            "difficulty": forms.Select(attrs={
                "class": "form-control",
                "dir": "rtl",
            }),
            "questions": forms.NumberInput(attrs={
                "class": "form-control",
                "data-plugin":"touchSpin",
                "dir": "rtl",
            }),
        }


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

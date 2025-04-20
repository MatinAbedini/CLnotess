from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django import forms

from .models import *
from utils.form_fields import MultipleFileField


class ExamForm(forms.ModelForm):
    assigned_to = forms.MultipleChoiceField(
        required=True,
        label=_("برای کلاس"),
        widget=forms.SelectMultiple(attrs={
            "class": "form-control",
            "dir": "rtl",
        })
    )

    class Meta:
        model = Exam
        fields = ("title", "description", "for_date", "duration", "difficulty", "lesson", "questions")
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
            "lesson": forms.Select(attrs={
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
    files = MultipleFileField(label=_("فایل ها"))
    student = forms.ChoiceField(
        required=True,
        label=_("دانش آموز"),
        widget=forms.Select(attrs={
            "class": "form-control",
            "dir": "rtl",
        })
    )

    class Meta:
        model = ExamResult
        fields = ("description", "correct_answers", "not_answered", "incorrect_answers", "result")
        widgets = {
            "correct_answers": forms.NumberInput(attrs={
                "class": "form-control",
                "dir": "rtl",
            }),

            "not_answered": forms.NumberInput(attrs={
                "class": "form-control",
                "dir": "rtl",
            }),

            "incorrect_answers": forms.NumberInput(attrs={
                "class": "form-control",
                "dir": "rtl",
            }),

            "result": forms.Select(attrs={
                "class": "form-control",
                "dir": "rtl",
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "dir": "rtl",
            })
        }

    def __init__(self, *args, **kwargs):
        # Makes files optional or required,
        # Depending of entered value of files_required in form kwargs.

        files_required = kwargs.pop("files_required", True)
        super().__init__(*args, **kwargs)

        if not files_required:
            self.fields.get("files").required = False

    def clean_files(self):
        # Saves files uploaded files and max amount of file (25 files)

        files = self.files.getlist("files")
        max_file = 25

        # If uploaded files are more thant max_file raises a validation error
        # Else returns the files (No error)

        if len(files) > max_file:
            raise ValidationError(_(".شما بیشتر از 25 فایل نمی توانید آپلود کنید"))

        return files


class ExamFeedbackForm(forms.ModelForm):
    files = MultipleFileField(label=_("فایل ها"))

    class Meta:
        model = ExamFeedback
        fields = ("description",)
        widgets = {
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "dir": "rtl",
            })
        }

    def __init__(self, *args, **kwargs):
        # Makes files optional or required,
        # Depending of entered value of files_required in form kwargs.

        files_required = kwargs.pop("files_required", True)
        super().__init__(*args, **kwargs)

        if not files_required:
            self.fields.get("files").required = False

    def clean_files(self):
        # Saves files uploaded files and max amount of file (25 files)

        files = self.files.getlist("files")
        max_file = 25

        # If uploaded files are more thant max_file raises a validation error
        # Else returns the files (No error)

        if len(files) > max_file:
            raise ValidationError(_(".شما بیشتر از 25 فایل نمی توانید آپلود کنید"))

        return files

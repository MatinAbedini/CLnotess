from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django import forms

from utils.form_fields import MultipleFileField
from .models import *


class HomeworkForm(forms.ModelForm):
    assigned_to = forms.MultipleChoiceField(
        required=True,
        label=_("برای کلاس"),
        widget=forms.SelectMultiple(attrs={
            "class": "form-control",
            "dir":"rtl"
        })
    )

    class Meta:
        model = Homework
        fields = ("title", "lesson", "description", "for_date")
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "dir":"rtl",
            }),
            "lesson": forms.Select(attrs={
                "class": "form-control",
                "dir": "rtl",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": "3",
                "dir":"rtl",
            }),
            "for_date": forms.TextInput(attrs={
                "class": "form-control",
                "data-mask": "9999-99-99",
                "data-plugin":"touchSpin",
            }),
        }


class HomeworkResultForm(forms.ModelForm):
    files = MultipleFileField(label=_("فایل ها"))

    class Meta:
        model = HomeworkResult
        fields = ("description",)
        labels = {"description": _("توضیحات")}
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
        """If uploaded files are more that 25, raises a validation error"""

        # Save files and max_files
        files = self.files.getlist("files")
        max_file = 25

        # If uploaded file are more thant 25 raises a validation error
        if len(files) > max_file:
            raise ValidationError(_(".شما بیشتر از 25 فایل نمی توانید آپلود کنید"))

        return files


class HomeworkFeedbackForm(forms.ModelForm):
    files = MultipleFileField(label=_("فایل ها"))

    class Meta:
        model = HomeworkFeedback
        fields = ("description",)
        labels = {"description": _("توضیحات")}
        widgets = {
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "dir": "rtl",
            })
        }

    def __init__(self, *args, **kwargs):
        files_required = kwargs.pop("files_required", True)
        super().__init__(*args, **kwargs)

        if not files_required:
            self.fields.get("files").required = False

    def clean_files(self):
        """If uploaded files are more that 25, raises a validation error"""

        # Save files and max_files
        files = self.files.getlist("files")
        max_file = 25

        # If uploaded file are more thant 25 raises a validation error
        if len(files) > max_file:
            raise ValidationError(_(".شما بیشتر از 25 فایل نمی توانید آپلود کنید"))

        return files

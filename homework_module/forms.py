from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django_jalali import forms as jforms
from django import forms
from .models import *


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


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
    homework = forms.ChoiceField(
        required=True,
        label=_("تکلیف"),
        widget=forms.Select(attrs={
            "class": "form-control",
            "dir": "rtl",
        })
    )

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
        show_homework = kwargs.pop("show_homework", False)

        super().__init__(*args, **kwargs)

        if not show_homework:
            self.fields.pop("homework")

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
    homework = forms.ChoiceField(
        required=True,
        label=_("تکلیف"),
        widget=forms.Select(attrs={
            "class": "form-control",
            "dir": "rtl",
        })
    )

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
        show_homework = kwargs.pop("show_homework", False)

        super().__init__(*args, **kwargs)

        if not show_homework:
            self.fields.pop("homework")

    def clean_files(self):
        """If uploaded files are more that 25, raises a validation error"""

        # Save files and max_files
        files = self.files.getlist("files")
        max_file = 25

        # If uploaded file are more thant 25 raises a validation error
        if len(files) > max_file:
            raise ValidationError(_(".شما بیشتر از 25 فایل نمی توانید آپلود کنید"))

        return files

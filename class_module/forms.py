from django.utils.translation import gettext_lazy as _
from django.forms import ValidationError
from django import forms
from typing import Any
from .models import Class


class ClassForm(forms.ModelForm):
    students = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "data-role":"tagsinput",
            "placeholder":"اضافه کردن دانش آموز",
        })
    )

    teachers = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "data-role":"tagsinput",
            "placeholder":"اضافه کردن معلم",
        })
    )


    class Meta:
        model = Class
        fields = ("class_name", "school_name")
        widgets = {
            "class_name": forms.TextInput(attrs={"class": "form-control"}),
            "school_name": forms.TextInput(attrs={"class": "form-control"})
        }


    def clean_students(self) -> Any | ValidationError:
        students = self.cleaned_data.get("students")
        if len(students) > 50:
            raise ValidationError(_("َشما نمی توانید بیش تر از 50 دانش آموز انتخاب کنید."))

        return students

    def clean_teachers(self) -> Any | ValidationError:
        students = self.cleaned_data.get("teachers")
        if len(students) > 50:
            raise ValidationError(_("َشما نمی توانید بیش تر از 50 معلم انتخاب کنید."))

        return students

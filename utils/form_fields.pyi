from typing import Any
from django import forms


class MultipleFileInput(forms.ClearableFileInput):
    ...


class MultipleFileField(forms.FileField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def clean(self, data: Any, initial: Any | None = None):
        ...

from django.utils.translation import gettext_lazy as _
from django.forms import ValidationError

from homework_module.models import Homework
from exam_module.models import Exam


class MaxFileSize:
    message = _(".حداکثر حجم فایل ها %(max_size) مگابایت است")
    code = "too_large"
    default_max_size = 5

    def __init__(self, max_size: int | None = None) -> None:
        if not max_size:
            max_size = self.default_max_size

        self.max_size = max_size * (1024 ** 2)

    def __call__(self, value):
        if value.size > self.max_size:
            raise ValidationError(
                message=self.message,
                code=self.code,
                params={
                    "max_size": self.max_size,
                }
            )

    def __eq__(self, other):
        return (
            isinstance(self, other) and
            self.default_max_size == other.default_max_size
        )


class MinFileSize:
    message = _(".حداقل حجم فایل ها %(min_size) مگابایت است")
    code = "too_small"
    default_min_size = 5

    def __init__(self, min_size: int | None = None) -> None:
        if not min_size:
            min_size = self.default_min_size

        self.min_size = min_size * (1024 ** 2)

    def __call__(self, value):
        if value.size < self.min_size:
            raise ValidationError(
                message=self.message,
                code=self.code,
                params={
                    "min_size": self.min_size,
                }
            )

    def __eq__(self, other):
        return (
            isinstance(self, other) and
            self.default_min_size == other.default_min_size
        )

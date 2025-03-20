from typing import Any
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db import models
import jdatetime
import datetime


class JDateTimeField(models.DateTimeField):
    description = _("Jalali Date Time")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value: Any) -> Any:
        if isinstance(value, jdatetime.datetime):
            value = value.togregorian()

        if isinstance(value, datetime.datetime):
            value = value.replace(tzinfo=None)
            value = value.replace(microsecond=0)

        return super().get_prep_value(value)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return jdatetime.datetime.fromgregorian(date=value)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        return name, path, args, kwargs

    def clean(self, value, model_instance):
        super().clean(value, model_instance)

        if not isinstance(value, datetime.datetime):
            raise ValidationError(_("مقدار وارد شده یک تاریخ و زمان معتبر نیست."))

        return value


class JDateField(models.DateField):
    description = _("Jalali Date")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return jdatetime.date.fromgregorian(value)

    def get_prep_value(self, value: Any) -> Any:
        if isinstance(value, jdatetime.date):
            value = value.togregorian()

        if isinstance(value, datetime.datetime):
            value = value.replace(microsecond=0, tzinfo=None)

        return super().get_prep_value(value)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        return name, path, args, kwargs

    def clean(self, value, model_instance):
        super().clean(value, model_instance)

        if not isinstance(value, datetime.date):
            raise ValidationError(_("مقدار وارد شده یک تاریخ معتبر نیست."))

        return value

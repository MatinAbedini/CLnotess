from django.utils.translation import gettext_lazy as _
from django.forms import ValidationError


def validate_file_size(files):
    """
    Validates files using their size

    Args:
        file: List of files.

    Raises:
        ValidationError: If the size of files is more than entered size
    """

    # Calculates the max size in MB
    max_size = 50 * 1024 * 1024 #

    # Raise an error if the size of files is more than entered size
    if files.size > max_size:
        raise ValidationError(_(".حداکثر حجم فایل ها 50 مگابایت است"))

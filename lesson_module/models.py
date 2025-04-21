from django.db import models

# Create your models here.


class Lesson(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False, unique=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    is_delete = models.BooleanField(default=False, db_index=True)

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        verbose_name = 'درس'
        verbose_name_plural = 'درس ها'

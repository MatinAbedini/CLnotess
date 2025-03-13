from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ExamModuleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exam_module'
    verbose_name = _('اپلیکیشن امتحانات')

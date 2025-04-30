from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class SampleExamModuleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sample_exam_module'
    verbose_name = _('اپلیکیشن نمونه سوالات امتحانی')

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NoteModuleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "note_module"
    verbose_name = _('اپلیکیشن نکات درسی')

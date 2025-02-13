from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HomeModuleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home_module'
    verbose_name = _('اپلیکیشن خانه')

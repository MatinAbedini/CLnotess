from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InvitationModuleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'invitation_module'
    verbose_name = _("اپلیکیشن دعوت ها")

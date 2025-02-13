from django.views.generic import TemplateView
from django.shortcuts import redirect, render
from django.urls import reverse

# Create your views here.

class UserPanelDashboard(TemplateView):
    template_name = "user_panel_module/user-panel-dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login-page"))

        return super().dispatch(request, *args, **kwargs)


def user_panel_menu_partial(request):
    return render(request, "user_panel_module/components/user-panel-menu-partial.html")

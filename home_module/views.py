from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.shortcuts import render

from site_module.models import SiteSettings
from .forms import ContactForm
from .models import Contact


# Create your views here.


class IndexView(CreateView):
    template_name = "home_module/index.html"
    success_url = reverse_lazy("index-page")
    form_class = ContactForm
    model = Contact

def navbar_partial(request):
    return render(request, "shared/partials/navbar.html")

def left_sidebar_partial(request):
    context = {
        "site_settings": SiteSettings.objects.get(is_main=True),
    }
    
    return render(request, "shared/partials/left-sidebar.html", context)

def right_sidebar_partial(request):
    return render(request, "shared/partials/right-sidebar.html")

def footer_partial(request):
    return render(request, "shared/partials/footer.html")

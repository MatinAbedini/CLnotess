from django.views.generic import TemplateView
from django.shortcuts import render


# Create your views here.


class IndexView(TemplateView):
    template_name = "home_module/index.html"


def navbar_partial(request):
    return render(request, "shared/partials/navbar.html")

def left_sidebar_partial(request):
    return render(request, "shared/partials/left-sidebar.html")

def right_sidebar_partial(request):
    return render(request, "shared/partials/right-sidebar.html")

def footer_partial(request):
    return render(request, "shared/partials/footer.html")

from django.urls import path, include

urlpatterns = [
    path("invitations/", include("invitation_module.urls")),
    path("homeworks/", include("homework_module.urls")),
    path("exams/", include("exam_module.urls")),
    path('classes/', include('class_module.urls')),
    path('panel/', include('user_panel_module.urls'),),
]

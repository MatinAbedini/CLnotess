from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from utils.class_service import add_students, add_teachers
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.http import HttpResponseForbidden
from django.urls import reverse, reverse_lazy
from .forms import ClassForm, AddUserForm
from .models import Class

# Create your views here.


class ClassCreateView(CreateView):
    form_class = ClassForm
    template_name = "class_module/create-class.html"
    success_url = reverse_lazy("index-page")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden(_("شما به این صفحه دسترسی ندارید."))

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        # If the class already exists, return an error

        new_Class_exists: bool = (
            Class.objects.filter(
                class_name=form.data.get("class_name"),
                school_name=form.data.get("school_name")
            )
            .exists()
        )

        if new_Class_exists:
            form.add_error("class_name", _("این کلاس قبلا ثبت شده است."))
            return self.form_invalid(form)


        # Save user and new class
        user = self.request.user
        new_class: Class = form.save(commit=False)
        new_class.created_by = user
        new_class.save()

        # save entered teachers and students
        students = form.data.get("students")
        teachers = form.data.get("teachers")

        # Assign the class to the user
        new_class.assigned_to.add(user)

        # Assigned the class to teachers and students
        # If teachers or students are not empty

        if teachers != "":
            add_teachers(new_class, user, teachers, False)
        if students != "":
            add_students(new_class, user, students, False)

        return super().form_valid(form)


class AddStudentView(CreateView):
    form_class = AddUserForm
    template_name = "class_module/add-student.html"
    success_url = reverse_lazy("index-page")


    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login-page"))

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.request.user
        students = form.cleaned_data.get("students")
        add_students(self.kwargs.get("uuid"), user, students)

        return super().form_valid(form)


class AddTeacherView(CreateView):
    form_class = AddUserForm
    template_name = "class_module/add-teacher.html"
    success_url = reverse_lazy("index-page")


    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login-page"))

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            user = self.request.user
            teachers, lesson = form.cleaned_data.get("teachers").split(" - ")
            add_teachers(self.kwargs.get("uuid"), user, teachers, lesson)

        except:
            form.add_error("teachers", _("لطفا معلم را به همراه درس مربوطه بنویسید و آنها را حتما با ' - ' جدا کنید. محد رضایی - شیمی"))
            return self.form_invalid(form)

        return super().form_valid(form)


class ClassListView(ListView):
    model = Class
    template_name = "class_module/class-list.html"
    context_object_name = "classes"
    ordering = "creation_date"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login-page"))

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        base_query = (
            Class.objects.filter(
                assigned_to=user,
                is_active=True,
                is_delete=False
            ).only("class_name", "school_name")
        )

        return base_query


@login_required
def delete_class(request, uuid):
    """
    Delete a class (Change is_delete to false),
    And Finds class using entered uuid in the url.
    if:
        1. User is authenticated
        2. The class is created by user
    """

    # Save the user
    # Save the class, if the user is assigned to the class

    user = request.user
    class_: Class = get_object_or_404(
        Class.objects.filter(
            created_by=user,
            is_active=True,
            is_delete=False,
            uuid=uuid
        )
        .only("is_delete")
    )

    # Delete the class (Change is_delete to false)
    # Redirect the user to previous url

    class_.is_delete = True
    class_.save()

    previous_url = request.META.get("HTTP_REFERER", None)

    if previous_url is None:
        return redirect(reverse("class-list-page"))

    return redirect(previous_url)


@login_required
def leave_class(request, uuid):
    """
    leave a class, and finds the class using entered uuid in the url.
    if:
        1. User is authenticated
        2. The class is not created by user
        3. The user is assigned to the class
    """

    # Save the user and the class
    # If the user is assigned to the class And the class is not created by the user

    user = request.user
    class_: Class = get_object_or_404(
        Class.objects.filter(
            assigned_to=user,
            is_active=True,
            is_delete=False,
            uuid=uuid
        )
        .exclude(created_by=user)
    )

    # Delete the class (Change is_delete to false)
    # Redirect the user to previous url

    class_.assigned_to.remove(user)
    previous_url = request.META.get("HTTP_REFERER", None)

    if previous_url is None:
        return redirect(reverse("class-list-page"))

    return redirect(previous_url)

from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView
from django.urls import reverse, reverse_lazy

from invitation_module.models import Invitation
from .forms import ClassForm
from .models import Class

# Create your views here.


class ClassCreateView(LoginRequiredMixin, CreateView):
    template_name = "class_module/create-class.html"
    success_url = reverse_lazy("class-list-page")
    form_class = ClassForm
    model = Class

    def form_valid(self, form):
        # If the class already exists, return an error

        duplicated_class = (
            Class.objects.filter(
                class_name=form.data.get("class_name"),
                school_name=form.data.get("school_name"),
                created_by=self.request.user,
                is_delete=True,
            )

        )

        if duplicated_class.exists():
            duplicated_class.is_delete = False
            duplicated_class.save()

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
            new_class.assign_users(user, teachers)
        if students != "":
            new_class.assign_users(user, students)

        return super().form_valid(form)


class ClassUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "class_module/edit-class.html"
    success_url = reverse_lazy("class-list-page")
    form_class = ClassForm
    model = Class
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def form_valid(self, form):
        # If the class already exists, return an error

        duplicated_class = (
            Class.objects.filter(
                class_name=form.data.get("class_name"),
                school_name=form.data.get("school_name"),
                created_by=self.request.user,
                is_delete=True,
            )

        )

        if duplicated_class.exists():
            duplicated_class.is_delete = False
            duplicated_class.save()

            return self.form_invalid(form)


        # Save user and new class
        user = self.request.user
        new_class: Class = form.save(commit=False)

        # save entered teachers and students
        students = form.data.get("students")
        teachers = form.data.get("teachers")

        # Assigned the class to teachers and students
        # If teachers or students are not empty

        if teachers != "":
            new_class.assign_users(user, teachers)
        if students != "":
            new_class.assign_users(user, students)

        return super().form_valid(form)


class ClassListView(LoginRequiredMixin, ListView):
    template_name = "class_module/class-list.html"
    context_object_name = "classes"
    model = Class
    ordering = "creation_date"
    paginate_by = 10

    def get_queryset(self):
        if not hasattr(self, "base_query"):
            self.base_query = (
                Class.objects.filter(
                    assigned_to=self.request.user,
                    is_delete=False,
                ).only("class_name", "school_name")
            )

        return self.base_query


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

from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic.edit import FormView, CreateView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.urls import reverse, reverse_lazy
from django.http import FileResponse, HttpRequest
from django.db.models import Q

from account_module.models import Account
from class_module.models import Class
from lesson_module.models import Lesson
from .models import *
from .forms import *


# Create your views here.


class HomeworkCreateView(FormView):
    model = Homework
    form_class = HomeworkForm
    template_name = "homework_module/create-homework.html"
    success_url = reverse_lazy("homework-list-page")


    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login-page"))

        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        user = self.request.user
        classes = (
            Class.objects.filter(
                Q(teachers__teacher=user) | Q(created_by=user),
                is_active=True,
                is_delete=False
            ).only("class_name", "school_name", "id")
        )

        form: HomeworkForm = super().get_form(form_class)
        class_choices = [(class_.uuid, class_.__str__) for class_ in classes]
        form.fields["assigned_to"].choices = class_choices

        return form

    def form_valid(self, form: HomeworkForm):
        new_homework: Homework = form.save(commit=False)
        assigned_to_list: list[str] = form.cleaned_data.get("assigned_to")

        classes = Class.objects.filter(
            uuid__in=assigned_to_list,
            is_active=True,
            is_delete=False
        ).prefetch_related("assigned_to")

        if not classes.exists():
            return super().form_valid(form)

        homework_assigned_to_list = [
            HomeworkCreatedFor(
                homework=new_homework,
                assigned_to=student,
                status=3
            )
            for class_ in classes
            for student in class_.assigned_to.all()
        ]

        new_homework.created_by = self.request.user
        new_homework.save()
        HomeworkCreatedFor.objects.bulk_create(homework_assigned_to_list)

        return super().form_valid(form)


class HomeworkUpdateView(UpdateView):
    template_name = "homework_module/edit-homework.html"
    success_url = reverse_lazy("index-page")
    form_class = HomeworkForm
    model = Homework
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated and self:
            return redirect(reverse("login-page"))

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        base_query = Homework.objects.filter(
            uuid=self.kwargs.get("uuid"),
            is_delete=False,
        )

        return base_query

    def get_form(self, form_class=None):
        classes = (
            Class.objects.filter(
                teachers__teacher=self.request.user,
                is_active=True,
                is_delete=False
            ).only("class_name", "school_name", "uuid")
        )

        form = super().get_form(form_class)
        class_choices = [(class_.uuid, class_) for class_ in classes]
        form.fields["assigned_to"].choices = class_choices
        return form


class HomeworkListView(ListView):
    model = HomeworkCreatedFor
    template_name = "homework_module/homework-list.html"
    context_object_name = "homeworks"
    ordering = "status"
    paginate_by = 10

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login-page"))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lessons = Lesson.objects.all().only("name")

        context["status_filter"] = self.request.GET.get("status", "")
        context["lesson_filter"] = self.request.GET.get("lesson", "")
        context["lessons"] = [lesson.name for lesson in lessons]

        return context

    def get_queryset(self):
        user = self.request.user
        status_filter: str = self.request.GET.get("status", "")
        lesson_filter: str = self.request.GET.get("lesson", "")

        base_query = (
            HomeworkCreatedFor.objects.filter(
                assigned_to=user,
                homework__is_delete=False,
            )
        )

        if status_filter != "":
            status_filter = list(map(int, status_filter.split(",")))
            base_query = base_query.filter(status__in=status_filter)

        if lesson_filter != "":
            lesson_filter = lesson_filter.split(",")
            base_query = base_query.filter(homework__lesson__name__in=lesson_filter)

        return base_query


class HomeworkDetailView(DetailView):
    model = HomeworkCreatedFor
    template_name = "homework_module/homework.html"
    context_object_name = "homework"
    slug_url_kwarg = "uuid"
    slug_field = "uuid"

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login-page"))

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        base_query = (
            HomeworkCreatedFor.objects.filter(
                assigned_to=user,
                homework__is_delete=False
            )
        )

        return base_query


class HomeworkResultCreateView(CreateView):
    form_class = HomeworkResultForm
    template_name =  "homework_module/create-homework-result.html"
    success_url = reverse_lazy("homework-list-page")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login-page"))

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        # Show homework field if uuid is in url (kwargs)
        kwargs = super().get_form_kwargs()

        if not "uuid" in self.kwargs:
            kwargs["show_homework"] = True

        return kwargs

    def get_form(self, form_class=None):
        # If uuid is not in url (kwargs), show homework field
        if "uuid" in self.kwargs:
            return super().get_form(form_class)

        # Save User and assigned homeworks to the user
        user = self.request.user
        homeworks = (
            HomeworkCreatedFor.objects.filter(
                homework__created_by=user,
                homework__is_delete=False
            )
            .prefetch_related("homework")
            .only("homework__title", "uuid")
        )

        # Add assigned homeworks to homework field as choices
        form = super().get_form(form_class)
        homework_choices = [(homework.uuid, homework.homework.title) for homework in homeworks]
        form.fields["homework"].choices = homework_choices

        return form

    def form_valid(self, form):
        # Save HomeworkCreatedFor (Specified homework),
        # Using entered uuid in the url or selected uuid in form

        homework_uuid = self.kwargs.get("uuid", form.cleaned_data.get("homework"))
        homework: HomeworkCreatedFor = (
            HomeworkCreatedFor.objects.filter(
                uuid=homework_uuid,
                homework__is_delete=False
            )
            .only("result")
            .first()
        )

        # Save assigned files to result as a list
        # Save new homework result and set it as result of HomeworkCreatedFor

        files = self.request.FILES.getlist("files")
        homework_result = form.save()
        homework.result = homework_result
        homework.save()

        # Upload and save assigned files to result in server

        homework_result_files = [
            HomeworkResultFile(
                homework=homework_result,
                file=file
            )
            for file in files
        ]

        HomeworkResultFile.objects.bulk_create(homework_result_files)

        return super().form_valid(form)


class HomeworkResultUpdateView(UpdateView):
    model = HomeworkResult
    form_class = HomeworkResultForm
    template_name = "homework_module/edit-homework-result.html"
    success_url = reverse_lazy("index-page")
    context_object_name = "homework_result"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"


    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login-page"))

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        base_query = super().get_queryset()
        base_query = base_query.filter(
            is_delete=False
        )

        return base_query

    def get_form(self, form_class=None):
        user = self.request.user

        homeworks = (
            Homework.objects.filter(
                created_by=user,
                is_delete=False
            )
            .only("title", "uuid")
        )
        students = (
            set(
                Account.objects.filter(
                    assigned_classes__teachers__teacher=user,
                    is_active=True,
                )
                .only("username", "active_code")
            )
        )

        form = super().get_form(form_class)
        homework_choices = [(homework.uuid, homework.title) for homework in homeworks]
        student_choices = [
            (student.active_code, student.username)
            for student in students
        ]

        form.fields["homework"].choices = homework_choices
        form.fields["student"].choices = student_choices

        return form

    def form_valid(self, form):
        homework_result = form.save(commit=False)
        homework_result.homework = (
            Homework.objects.get(
                uuid=form.cleaned_data.get("homework"),
                is_delete=False
            )
        )
        homework_result.student = (
            Account.objects.get(
                active_code=form.cleaned_data.get("student"),
                is_active=True
            )
        )

        return super().form_valid(form)


class HomeworkResultFileListView(ListView):
    model = HomeworkResultFile
    template_name = "homework_module/homework-result-file-list.html"
    context_object_name = "files"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login-page"))

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        base_query = (
            HomeworkResultFile.objects.filter(
                is_delete=False
            )
            .prefetch_related("homework")
            .only("file", "homework")
        )

        uuid = self.kwargs.get("uuid")

        if uuid is not None:
            base_query.filter(homework__homework__uuid=uuid)

        return base_query


class HomeworkFeedbackCreateView(CreateView):
    form_class = HomeworkResultForm
    template_name =  "homework_module/create-homework-result.html"
    success_url = reverse_lazy("index-page")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login-page"))

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        # Show homework field if uuid is in url (kwargs)
        kwargs = super().get_form_kwargs()
        kwargs["show_homework"] = True

        return kwargs

    def get_form(self, form_class=None):
        # If uuid is not in url (kwargs), show homework field
        if "uuid" in self.kwargs:
            return super().get_form(form_class)

        # Save User and assigned homeworks to the user
        user = self.request.user
        homeworks = (
            Homework.objects.filter(
                created_by=user,
                is_delete=False
            )
            .only("title", "uuid")
        )

        # Add assigned homeworks to homework field as choices
        form = super().get_form(form_class)
        homework_choices = [(homework.uuid, homework.title) for homework in homeworks]
        form.fields["homework"].choices = homework_choices

        return form

    def form_valid(self, form):
        homework_result = form.save(commit=False)

        # If uuid is not in url (kwargs), show homework field
        # if "uuid" in self.kwargs:
        #     homework = Homework.objects.get(
        #         uuid=self.kwargs["uuid"],
        #         is_active=True,
        #         is_delete=False
        #     )

        homework_result.homework = (
            Homework.objects.get(
                uuid=form.cleaned_data.get("homework"),
                is_delete=False
            )
        )

        return super().form_valid(form)
        print(form.cleaned_data)
        return super().form_invalid(form)


class HomeworkFeedbackUpdateView(UpdateView):
    model = HomeworkResult
    form_class = HomeworkResultForm
    template_name = "homework_module/edit-homework-result.html"
    success_url = reverse_lazy("index-page")
    context_object_name = "homework_result"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"


    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login-page"))

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        base_query = super().get_queryset()
        base_query = base_query.filter(
            is_delete=False
        )

        return base_query

    def get_form(self, form_class=None):
        user = self.request.user

        homeworks = (
            Homework.objects.filter(
                created_by=user,
                is_delete=False
            )
            .only("title", "uuid")
        )
        students = (
            set(
                Account.objects.filter(
                    assigned_classes__teachers__teacher=user,
                    is_active=True,
                )
                .only("username", "active_code")
            )
        )

        form = super().get_form(form_class)
        homework_choices = [(homework.uuid, homework.title) for homework in homeworks]
        student_choices = [
            (student.active_code, student.username)
            for student in students
        ]

        form.fields["homework"].choices = homework_choices
        form.fields["student"].choices = student_choices

        return form

    def form_valid(self, form):
        homework_result = form.save(commit=False)
        homework_result.homework = (
            Homework.objects.get(
                uuid=form.cleaned_data.get("homework"),
                is_delete=False
            )
        )
        homework_result.student = (
            Account.objects.get(
                active_code=form.cleaned_data.get("student"),
                is_active=True
            )
        )

        return super().form_valid(form)


class HomeworkFeedbackFileListView(ListView):
    model = HomeworkResultFile
    template_name = "homework_module/homework-result-file-list.html"
    context_object_name = "files"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login-page"))

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        base_query = (
            HomeworkResultFile.objects.filter(
                is_delete=False
            )
            .prefetch_related("homework")
            .only("result_file", "homework")
        )

        uuid = self.kwargs.get("uuid")

        if uuid is not None:
            base_query.filter(uuid=uuid)

        return base_query


@login_required
def done_homework(request, uuid):
    """
    Changes the status of a homework to done, using entered uuid in the url,
    if:
        1. User is authenticated
        2. The homework is assigned to user
    """

    # Save the user
    # Save homework, if its assigned to user

    user = request.user
    homework: HomeworkCreatedFor = get_object_or_404(
        HomeworkCreatedFor.objects.filter(
            assigned_to=user,
            homework__is_delete=False,
            uuid=uuid
        )
        .exclude(status=1)
        .only("status")
    )

    # Change the status of homework
    # Redirect the user to previous url

    homework.status = 1
    homework.save()

    previous_url = request.META.get("HTTP_REFERER", None)

    if previous_url is None:
        return redirect(reverse("homework-list-page"))

    return redirect(previous_url)

@login_required
def in_progress_homework(request, uuid):
    """
    Changes the status of a homework to in progress,
    using entered uuid in the url,
    if:
        1. User is authenticated
        2. The homework is assigned to user
    """

    # Save the user
    # Save homework, if its assigned to user

    user = request.user
    homework: HomeworkCreatedFor = get_object_or_404(
        HomeworkCreatedFor.objects.filter(
            assigned_to=user,
            homework__is_delete=False,
            uuid=uuid
        )
        .exclude(status=2)
        .only("status")
    )

    # Change the status of homework
    # Redirect the user to previous url or homework list page

    homework.status = 2
    homework.save()

    previous_url = request.META.get("HTTP_REFERER", None)

    if previous_url is None:
        return redirect(reverse("homework-list-page"))

    return redirect(previous_url)

@login_required
def not_done_homework(request, uuid):
    """
    Changes the status of a homework to not done, using entered uuid in the url,
    if:
        1. User is authenticated
        2. The homework is assigned to user
    """

    # Save the user
    # Save homework, if its assigned to user

    user = request.user
    homework: HomeworkCreatedFor = get_object_or_404(
        HomeworkCreatedFor.objects.filter(
            assigned_to=user,
            homework__is_delete=False,
            uuid=uuid
        )
        .exclude(status=3)
        .only("status")
    )

    # Change the status of homework
    # Redirect the user to previous url or homework list page

    homework.status = 3
    homework.save()

    previous_url = request.META.get("HTTP_REFERER", None)

    if previous_url is None:
        return redirect(reverse("homework-list-page"))

    return redirect(previous_url)

@login_required
def delete_homework(request, uuid):
    """
    Delete a homework (Change is_delete to false),
    And Finds homework using entered uuid in the url,
    if:
        1. User is authenticated
        2. The homework is assigned to user
    """

    # Save the user
    # Save homework, if its assigned to user

    user = request.user
    homework: Homework = get_object_or_404(
        Homework.objects.filter(
            created_by=user,
            is_delete=False,
            uuid=uuid
        )
        .only("is_delete")
    )

    # Delete the homework (Change is_delete to false)
    # Redirect the user to previous url

    homework.is_delete = True
    homework.save()

    return redirect(reverse("homework-list-page"))

@login_required
def download_homework_result(request, url_path):
    """
    Delete a homework (Change is_delete to false),
    And Finds homework using entered uuid in the url,
    if:
        1. User is authenticated
        2. The homework is assigned to user
    """

    # Save the user
    # Save homework, if its assigned to user
    user = request.user
    result = get_object_or_404(
        HomeworkResultFile,
        Q(homework__homework__assigned_to=user) | Q(homework__homework_homework__created_by=user),
        file__url_path=url_path
    )

    return FileResponse(result.file.open("rb"), as_attachment=True)

@login_required
def download_homework_feedback(request, url_path):
    """
    Delete a homework (Change is_delete to false),
    And Finds homework using entered uuid in the url,
    if:
        1. User is authenticated
        2. The homework is assigned to user
    """

    # Save the user
    # Save homework, if its assigned to user
    result = get_object_or_404(HomeworkResult, uuid=uuid)

    return FileResponse(result.result_file.open('rb'), as_attachment=True)

def filter_tab(request):
    return render(request, "homework_module/components/filter-tab.html")

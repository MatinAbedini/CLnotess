from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic.edit import FormView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.urls import reverse, reverse_lazy
from django.http import FileResponse
from django.core.paginator import Paginator
from django.db.models import Q

from account_module.models import Account
from class_module.models import Class
from lesson_module.models import Lesson
from .models import *
from .forms import *


# Create your views here.


class HomeworkCreateView(LoginRequiredMixin, FormView):
    template_name = "homework_module/create-homework.html"
    success_url = reverse_lazy("homework-list-page")
    form_class = HomeworkForm
    model = Homework

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
                assigned_class=class_,
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


class HomeworkUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "homework_module/edit-homework.html"
    success_url = reverse_lazy("homework-list-page")
    form_class = HomeworkForm
    model = Homework
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def get_queryset(self):
        base_query = Homework.objects.filter(
            uuid=self.kwargs.get("uuid"),
            is_delete=False,
        )

        return base_query

    def get_form(self, form_class=None):
        user = self.request.user

        classes = (
            Class.objects.filter(
                Q(teachers__teacher=user) | Q(created_by=user),
                is_active=True,
                is_delete=False
            ).only("class_name", "school_name", "uuid")
        )

        form = super().get_form(form_class)
        class_choices = [(class_.uuid, class_) for class_ in classes]
        form.fields["assigned_to"].choices = class_choices
        return form

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user

        classes = (
            Class.objects.filter(
                Q(teachers__teacher=user) | Q(created_by=user),
                student_homeworks__homework=self.get_queryset().first(),
                is_delete=False,
            )
            .only("uuid")
        )

        initial["assigned_to"] = [class_.uuid for class_ in classes]

        return initial


class HomeworkListView(LoginRequiredMixin, ListView):
    template_name = "homework_module/homework-list.html"
    context_object_name = "homeworks"
    model = HomeworkCreatedFor
    ordering = "status"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        # Save default contexts, lessons, classes
        context = super().get_context_data(**kwargs)
        lessons = Lesson.objects.all().only("name")
        homeworks = self.get_queryset()
        classes = [str(homework.assigned_class) for homework in homeworks]

        # Save status, lesson and classes which are going to get filtered
        # And save lessons, classes and those filters in context

        context["status_filter"] = self.request.GET.get("status", "")
        context["lesson_filter"] = self.request.GET.get("lesson", "")
        context["class_filter"] = self.request.GET.get("class_", "")
        context["lessons"] = [lesson.name for lesson in lessons]
        context["classes"] = classes

        return context

    def get_queryset(self):
        # If the queryset isn't cached, save the queryset and cache it
        # Else returns the cached values

        if not hasattr(self, "base_query"):
            # Save user and used filters
            # Filters assigned and not deleted homeworks

            user = self.request.user
            status_filter: str = self.request.GET.get("status", "")
            lesson_filter: str = self.request.GET.get("lesson", "")
            class_filter: str = self.request.GET.get("class_", "")

            self.base_query = (
                HomeworkCreatedFor.objects.filter(
                    assigned_to=user,
                    homework__is_delete=False,
                )
            )

            # Filter exams by status and lesson field,
            # If user has filter exams using them

            if status_filter != "":
                status_filter = list(map(int, status_filter.split(",")))
                self.base_query = self.base_query.filter(status__in=status_filter)

            if lesson_filter != "":
                lesson_filter = lesson_filter.split(",")
                self.base_query = self.base_query.filter(homework__lesson__name__in=lesson_filter)

            if class_filter != "":
                class_filter = class_filter.split(",")
                self.base_query = self.base_query.filter(class__str__in=class_filter)

        return self.base_query


class HomeworkDetailView(LoginRequiredMixin, DetailView):
    template_name = "homework_module/homework.html"
    context_object_name = "homework"
    model = HomeworkCreatedFor
    slug_url_kwarg = "uuid"
    slug_field = "uuid"

    def get_queryset(self):
        # If the queryset isn't cached, save the queryset and cache it
        # Else returns the cached values

        if hasattr(self, "base_query"):
            self.base_query = (
                HomeworkCreatedFor.objects.filter(
                    uuid=self.kwargs.get("uuid"),
                    assigned_to=self.request.user,
                    homework__is_delete=False
                )
                .select_related("homework", "result", "feedback")
            )

            return self.base_query

        return self.base_query


class HomeworkResultCreateView(LoginRequiredMixin, CreateView):
    form_class = HomeworkResultForm
    template_name =  "homework_module/create-homework-result.html"
    success_url = reverse_lazy("homework-list-page")

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
        # Using entered uuid in the url, or selected homework in the form

        homework_uuid = self.kwargs.get("uuid", form.cleaned_data.get("homework"))
        homework: HomeworkCreatedFor = (
            HomeworkCreatedFor.objects.filter(
                uuid=homework_uuid,
                homework__is_delete=False
            )
            .only("result")
            .first()
        )

        # Save assigned files to the result as a list
        # Save new homework_result, and set it as feedback of HomeworkCreatedFor

        files = self.request.FILES.getlist("files")
        homework_result = form.save()
        homework.result = homework_result
        homework.save()

        # Upload and save, homework_result files in server

        homework_result_files = [
            HomeworkResultFile(
                homework=homework_result,
                file=file
            )
            for file in files
        ]

        HomeworkResultFile.objects.bulk_create(homework_result_files)

        return super().form_valid(form)


class HomeworkResultUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "homework_module/edit-homework-result.html"
    success_url = reverse_lazy("index-page")
    context_object_name = "homework_result"
    form_class = HomeworkResultForm
    model = HomeworkResult
    slug_url_kwarg = "uuid"
    slug_field = "homework__uuid"

    def get_queryset(self):
        base_query = (
            HomeworkResult.objects.filter(
                homework__uuid=self.kwargs.get("uuid"),
                homework__assigned_to=self.request.user,
                homework__homework__is_delete=False
            )
        )

        return base_query

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


class HomeworkResultDetailView(LoginRequiredMixin, DetailView):
    template_name = "homework_module/homework-result.html"
    context_object_name = "homework"
    model = HomeworkCreatedFor
    slug_url_kwarg = "uuid"
    slug_field = "uuid"

    def get_queryset(self):
        if not hasattr(self, "base_query"):
            self.base_query = (
                HomeworkCreatedFor.objects.filter(
                    uuid=self.kwargs.get("uuid"),
                    homework__created_by=self.request.user,
                    homework__is_delete=False
                    )
                .select_related("homework", "result", "feedback")
            )

        return self.base_query

    def get_context_data(self, **kwargs):
        # Save default contexts, base_query (specified HomeworkCreatedFor) and page
        context = super().get_context_data(**kwargs)
        base_query = self.get_queryset().first()
        page = self.request.GET.get("page", 1)

        # Convert the page number from str to int
        # If can't convert it, because page number is not a number set page first page

        try:
            page = int(page)
        except ValueError:
            page = 1

        # Save every other HomeworkCreatedFor of that homework,
        # If the homework is not deleted and its created by user

        homeworks = (
            HomeworkCreatedFor.objects.filter(
                homework=base_query.homework,
                homework__created_by=self.request.user,
                homework__is_delete=False,
            )
            .exclude(result=None)
            .select_related("homework", "feedback", "result")
        )


        # If at least one person has submitted a homework_result
        # Paginate homeworks (One in each page)
        # Send result and feedback of that page with page_obj
        # Else Send Null for result and feedback

        if not homeworks.exists():
            context["result"] = None
            context["feedback"] = None

            return context

        paginator = Paginator(homeworks, 1)
        page_obj = paginator.page(page)
        homework = page_obj.object_list[0]

        context["result"] = homework.result
        context["feedback"] = homework.feedback
        context["page_obj"] = page_obj

        return context


class HomeworkResultFileListView(LoginRequiredMixin, ListView):
    template_name = "homework_module/homework-result-file-list.html"
    context_object_name = "files"
    model = HomeworkResultFile

    def get_queryset(self):
        base_query = (
            HomeworkResultFile.objects.filter(
                # homework__homework__uuid=self.kwargs.get("uuid"),
                is_delete=False,
            )
            .prefetch_related("homework")
            .only("file", "homework")
        )

        uuid = self.kwargs.get("uuid")

        if uuid is not None:
            base_query.filter(homework__homework__uuid=uuid)

        return base_query


class HomeworkFeedbackCreateView(LoginRequiredMixin, CreateView):
    form_class = HomeworkFeedbackForm
    template_name =  "homework_module/create-homework-feedback.html"
    success_url = reverse_lazy("homework-list-page")

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
            .only("feedback")
            .first()
        )

        # Save assigned files to the feedback as a list
        # Save new homeworK_feedback and set it as feedback of HomeworkCreatedFor

        files = self.request.FILES.getlist("files")
        homework_feedback = form.save()
        homework.feedback = homework_feedback
        homework.save()

        # Upload and save, homework_feedback files in server

        homework_feedback_files = [
            HomeworkFeedbackFile(
                homework=homework_feedback,
                file=file
            )
            for file in files
        ]

        HomeworkFeedbackFile.objects.bulk_create(homework_feedback_files)

        return super().form_valid(form)


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
    homework: HomeworkCreatedFor = (
        HomeworkCreatedFor.objects.filter(
            assigned_to=user,
            homework__is_delete=False,
            uuid=uuid
        )
        .exclude(status=1)
        .only("status")
        .first()
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
    homework: HomeworkCreatedFor = (
        HomeworkCreatedFor.objects.filter(
            assigned_to=user,
            homework__is_delete=False,
            uuid=uuid
        )
        .exclude(status=2)
        .only("status")
        .first()
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
    homework: HomeworkCreatedFor = (
        HomeworkCreatedFor.objects.filter(
            assigned_to=user,
            homework__is_delete=False,
            uuid=uuid
        )
        .exclude(status=3)
        .only("status")
        .first()
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
def complete_homework(request, uuid):
    """
    Changes the result status of a homework_result to complete,
    and finds it using entered uuid in the url,
    if:
        1. User is authenticated
        2. The homework created by user
    """

    # Save the user
    # Save homework, if its created by user

    user = request.user
    homework_result: HomeworkResult = (
        HomeworkResult.objects.filter(
            homework__homework__uuid=uuid,
            homework__homework__created_by=user,
            homework__homework__is_delete=False
        )
        .exclude(result_status=1)
        .only("result_status")
        .first()
    )

    # Change the status of homework_result
    # Redirect the user to previous url

    homework_result.result_status = 1
    homework_result.save()

    previous_url = request.META.get("HTTP_REFERER", None)

    if previous_url is None:
        return redirect(reverse("homework-list-page"))

    return redirect(previous_url)

@login_required
def waiting_homework(request, uuid):
    """
    Changes the result status of a homework_result to waitings,
    and finds it using entered uuid in the url,
    if:
        1. User is authenticated
        2. The homework created by user
    """

    # Save the user
    # Save homework, if its created by user

    user = request.user
    homework_result: HomeworkResult = (
        HomeworkResult.objects.get(
            homework__uuid=uuid,
            homework__assigned_to=user,
            homework__homework__is_delete=False
        )
        .exclude(result_status=2)
        .only("result_status")
    )

    # Change the result status of homework_result
    # Redirect the user to previous url or homework list page

    homework_result.result_status = 2
    homework_result.save()

    previous_url = request.META.get("HTTP_REFERER", None)

    if previous_url is None:
        return redirect(reverse("homework-list-page"))

    return redirect(previous_url)

@login_required
def not_complete_homework(request, uuid):
    """
    Changes the result status of a homework result to not completed,
    and finds it using entered uuid in the url,
    if:
        1. User is authenticated
        2. The homework is created by user
    """

    # Save the user
    # Save homework_result, if its created by user

    user = request.user
    homework_result: HomeworkResult = (
        HomeworkResult.objects.get(
            homework__uuid=uuid,
            homework__homework__created_by=user,
            homework__homework__is_delete=False
        )
        .exclude(result_status=3)
        .only("result_status")
    )

    # Change the result status of homework_result
    # Redirect the user to previous url or homework list page

    homework_result.result_status = 3
    homework_result.save()

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
    result = get_object_or_404(HomeworkResult, file__url=url_path)

    return FileResponse(result.result_file.open('rb'), as_attachment=True)

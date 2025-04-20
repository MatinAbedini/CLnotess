from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic.edit import FormView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.urls import reverse, reverse_lazy
from django.http.response import Http404
from django.http import HttpRequest
from django.db.models import Q

from lesson_module.models import Lesson
from class_module.models import Class
from .models import *
from .forms import *

# Create your views here.


class HomeworkCreateView(LoginRequiredMixin, FormView):
    template_name = "homework_module/create-homework.html"
    success_url = reverse_lazy("homework-list-page")
    form_class = HomeworkForm
    model = Homework

    def get_form(self, form_class=None):
        # If classes aren't cached (saved)
        # Save and find, classes which are created or assigned to user

        if not hasattr(self, "classes"):
            user = self.request.user
            self.classes = (
                Class.objects.filter(
                    Q(teacher=user) | Q(created_by=user),
                    is_delete=False,
                )
                .prefetch_related("student_homeworks", "assigned_to")
                .only("class_name", "school_name", "uuid")
            )

        # Add classes, as options to assigned_to, field in the form

        form: HomeworkForm = super().get_form(form_class)
        class_choices = [(class_.uuid, class_) for class_ in self.classes]
        form.fields["assigned_to"].choices = class_choices

        return form

    def form_valid(self, form: HomeworkForm):
        # Saves new homework and specified classes,
        # Which are going to get assigned by the homework (saved as classes var)

        homework: Homework = form.save(commit=False)
        assigned_to_list = form.cleaned_data.get("assigned_to")
        classes = self.classes.filter(uuid__in=assigned_to_list)

        # If classes doesn't exists, returns an error for assigned_to filled
        # And makes the form invalid

        if not classes.exists():
            form = self.get_form
            form.add_error("assigned_to", ".کلاس هایی که انتخاب کرده اید وجود ندارد")

            return super().form_invalid(form)

        # Sets created by of the homework to the user,
        # Assigns homework to specified classes,
        # And redirects the user to the default success url page (homework list page)

        homework.created_by = self.request.user
        homework.save()
        homework.assign_homework(classes)

        return super().form_valid(form)


class HomeworkUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "homework_module/edit-homework.html"
    success_url = reverse_lazy("homework-list-page")
    form_class = HomeworkForm
    model = Homework
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def get_queryset(self):
        # If the queryset isn't cached, it will save the queryset and cache it
        # Otherwise, it will return cached values

        if not hasattr(self, "base_query"):
            self.base_query = (
                Homework.objects.filter(
                    uuid=self.kwargs.get("uuid"),
                    created_by=self.request.user,
                    is_delete=False,
                )
            )

        return self.base_query

    def get_form(self, form_class=None):
        # Add classes, as options to assigned_to, field in the form

        self.base_query = self.base_query.first()
        form: HomeworkForm = super().get_form(form_class)
        class_choices = [(class_.uuid, class_) for class_ in self.classes]
        form.fields["assigned_to"].choices = class_choices

        return form

    def get_initial(self):
        # If classes aren't cached (saved)
        # Saves and finds, classes which are created or assigned to user

        if not hasattr(self, "classes"):
            user = self.request.user
            self.classes = (
                Class.objects.filter(
                    Q(teacher=user) | Q(created_by=user),
                    is_delete=False,
                )
                .prefetch_related("student_homeworks", "assigned_to")
                .only("class_name", "school_name", "uuid")
            )

        initial = super().get_initial()
        classes = (self.classes.filter(assigned_homeworks=self.get_queryset()))
        initial["assigned_to"] = [class_.uuid for class_ in classes]

        return initial

    def form_valid(self, form: HomeworkForm):
        # Saves modified homework, base homework (not modified version)
        # and specified classes, Which are going to get assigned by the homework (saved as classes var)

        new_homework: Homework = form.save(commit=False)
        old_homework: Homework = self.get_queryset()
        assigned_to_list = form.cleaned_data.get("assigned_to")
        classes = self.classes.filter(uuid__in=assigned_to_list)

        # If classes doesn't exists, returns an error for assigned_to filled
        # And makes the form invalid

        if not classes.exists():
            form = self.get_form
            form.add_error("assigned_to", ".کلاس هایی که انتخاب کرده اید وجود ندارد")

            return super().form_invalid(form)

        # Saves added and removed classes from base homework (not modified homework),
        # With finding differences on assigned classes of both homeworks (modified and not modified)
        # Assigns new homeworks and unassigns removed homeworks from homework

        new_homework_classes = set(
            new_homework.assigned_class.all().values_list("id", flat=True)
        )
        old_homework_classes = set(
            old_homework.assigned_class.all().values_list("id", flat=True)
        )

        added_classes = [
            new_homework_class

            for new_homework_class in new_homework_classes
            if not new_homework_class in old_homework_classes
        ]

        removed_classes = [
            old_homework_class

            for old_homework_class in old_homework_classes
            if not old_homework_class in new_homework_classes
        ]

        new_homework.assign_homework(added_classes)
        new_homework.unassign_homework(removed_classes)

        # Modifies every other modified fields, save Changes,
        # And at the end if the form is valid redirects the user to the default success url page
        # (homework list page)

        return super().form_valid(form)


class HomeworkListView(LoginRequiredMixin, ListView):
    template_name = "homework_module/homework-list.html"
    context_object_name = "homeworks"
    model = HomeworkCreatedFor
    ordering = "status"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        # Save default contexts and lessons
        context = super().get_context_data(**kwargs)
        lessons = Lesson.objects.all().only("name")

        # Save status and lesson which are going to get filtered
        # And save lessons, and those filters in context

        context["status_filter"] = self.request.GET.get("status", "")
        context["lesson_filter"] = self.request.GET.get("lesson", "")
        context["lessons"] = [lesson.name for lesson in lessons]

        return context

    def get_queryset(self):
        # If the queryset isn't cached, it will save the queryset and cache it
        # Otherwise, it will return cached values

        if not hasattr(self, "base_query"):
            self.base_query = (
                HomeworkCreatedFor.objects.filter(
                    assigned_to=self.request.user,
                    homework__is_delete=False,
                )
            )

        # Save user and used filters
        # Filters assigned and not deleted homeworks

        status_filter: str = self.request.GET.get("status", "")
        lesson_filter: str = self.request.GET.get("lesson", "")

        # Filter homeworks by status and lesson fields,
        # If user has filter homeworks using them

        if status_filter != "":
            status_filter = list(map(int, status_filter.split(",")))
            self.base_query = self.base_query.filter(status__in=status_filter)

        if lesson_filter != "":
            lesson_filter = lesson_filter.split(",")
            self.base_query = self.base_query.filter(homework__lesson__name__in=lesson_filter)

        return self.base_query


class HomeworkDetailView(LoginRequiredMixin, DetailView):
    template_name = "homework_module/homework.html"
    context_object_name = "homework"
    model = HomeworkCreatedFor
    slug_url_kwarg = "uuid"
    slug_field = "uuid"

    def get_queryset(self):
        # If the queryset isn't cached, it will save the queryset and cache it
        # Otherwise, it will return cached values

        if not hasattr(self, "base_query"):
            self.base_query = (
                HomeworkCreatedFor.objects.filter(
                    uuid=self.kwargs.get("uuid"),
                    assigned_to=self.request.user,
                    homework__is_delete=False,
                )
                .select_related("homework", "result", "feedback")
            )

        return self.base_query


class HomeworkResultCreateView(LoginRequiredMixin, CreateView):
    template_name =  "homework_module/create-homework-result.html"
    success_url = reverse_lazy("homework-list-page")
    form_class = HomeworkResultForm
    model = HomeworkResult

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(self, "homework"):
            # Save HomeworkCreatedFor (Specified homework),
            # Using entered uuid in the url, or selected homework in the form

            self.homework: HomeworkCreatedFor = (
                HomeworkCreatedFor.objects.get(
                    uuid=self.kwargs.get("uuid"),
                    assigned_to=self.request.user,
                    homework__is_delete=False
                )
            )

        if self.homework.result is not None:
            raise Http404(_("نتیجه تکلیف قبلا ثبت شده است."))

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Save assigned files to the result as a list
        # Save new homework_result, and set it as feedback of HomeworkCreatedFor

        files = self.request.FILES.getlist("files")
        homework_result = form.save()
        self.homework.result = homework_result
        self.homework.save()

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
    success_url = reverse_lazy("homework-list-page")
    context_object_name = "homework_result"
    form_class = HomeworkResultForm
    model = HomeworkResult
    slug_url_kwarg = "uuid"
    slug_field = "homework__uuid"

    def get_form_kwargs(self):
        # Makes files field optional
        kwargs = super().get_form_kwargs()
        kwargs["files_required"] = False

        return kwargs

    def form_valid(self, form):
        homework_result = form.save()
        new_files = self.request.FILES.getlist("files")
        old_files = homework_result.results.all()
        old_files.update(is_delete=True)

        # Upload and save, homework_result files in server

        homework_result_files = [
            HomeworkResultFile(
                homework=homework_result,
                file=file
            )
            for file in new_files
        ]

        HomeworkResultFile.objects.bulk_create(homework_result_files)

        return super().form_valid(form)

    def get_queryset(self):
        # If the queryset isn't cached, it will save the queryset and cache it
        # Otherwise, it will return cached values

        if not hasattr(self, "base_query"):
            self.base_query = (
                HomeworkResult.objects.filter(
                    homework__uuid=self.kwargs.get("uuid"),
                    homework__assigned_to=self.request.user,
                    homework__homework__is_delete=False
                )
            )

        return self.base_query


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
                    homework__is_delete=False,
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
                result__is_delete=False,
            )
            .exclude(result=None)
            .select_related("homework", "feedback", "result")
            .order_by("modify_date")
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

    def dispatch(self, request, *args, **kwargs):
        # Runs get_queryset function, so self.homework_result get created by the function
        # Saves the user

        self.get_queryset()
        user = self.request.user

        # If homework if self.homework_result is not created by user or assigned to user,
        # It will raise 404 page

        if self.homework_result.homework.homework.created_by != user and self.homework_result.homework.assigned_to != user:
            raise Http404(_("نتیجه امتحان موردنظر یافت نشد!"))

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if not hasattr(self, "base_query"):
            self.homework_result: HomeworkResult = (
                HomeworkResult.objects.get(
                    uuid=self.kwargs.get("uuid"),
                    homework__homework__is_delete=False,
                    is_delete=False,
                )
            )

            self.base_query = self.homework_result.results.filter(is_delete=False)

        return self.base_query


class HomeworkFeedbackCreateView(LoginRequiredMixin, CreateView):
    template_name =  "homework_module/create-homework-feedback.html"
    success_url = reverse_lazy("homework-list-page")
    form_class = HomeworkFeedbackForm
    model = HomeworkFeedback

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(self, "homework"):
            # Save HomeworkCreatedFor (Specified homework),
            # Using entered uuid in the url or selected uuid in form

            self.homework: HomeworkCreatedFor = (
                HomeworkCreatedFor.objects.get(
                    uuid=self.kwargs.get("uuid"),
                    homework__created_by=self.request.user,
                    homework__is_delete=False
                )
            )

        if self.homework.feedback is not None:
            raise Http404(_("بازخورد تکلیف قبلا ثبت شده است."))

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Save assigned files to the feedback as a list
        # Save new homeworK_feedback and set it as feedback of HomeworkCreatedFor

        files = self.request.FILES.getlist("files")
        homework_feedback = form.save()
        self.homework.feedback = homework_feedback
        self.homework.save()

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


class HomeworkFeedbackUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "homework_module/edit-homework-feedback.html"
    success_url = reverse_lazy("homework-list-page")
    context_object_name = "homework_feedback"
    form_class = HomeworkFeedbackForm
    model = HomeworkFeedback
    slug_url_kwarg = "uuid"
    slug_field = "homework__uuid"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["files_required"] = False

        return kwargs

    def get_queryset(self):
        if not hasattr(self, "base_query"):
            self.base_query = (
                HomeworkFeedback.objects.filter(
                    homework__uuid=self.kwargs.get("uuid"),
                    homework__assigned_to=self.request.user,
                    homework__homework__is_delete=False
                )
            )

        return self.base_query

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
        homework_feedback = form.save()
        new_files = self.request.FILES.getlist("files")
        old_files = homework_feedback.feedbacks.all()
        old_files.update(is_delete=True)

        # Upload and save, homework_feedback files in server

        homework_feedback_files = [
            HomeworkFeedbackFile(
                homework=homework_feedback,
                file=file
            )
            for file in new_files
        ]

        HomeworkFeedbackFile.objects.bulk_create(homework_feedback_files)

        return super().form_valid(form)


class HomeworkFeedbackFileListView(LoginRequiredMixin, ListView):
    template_name = "homework_module/homework-feedback-file-list.html"
    context_object_name = "files"
    model = HomeworkFeedbackFile

    def dispatch(self, request, *args, **kwargs):
        # Runs get_queryset function, so self.homework_result get created by the function
        # Saves the user

        self.get_queryset()
        user = self.request.user

        # If homework if self.homework_result is not created by user or assigned to user,
        # It will raise 404 page

        if self.homework_feedback.homework.homework.created_by != user and self.homework_feedback.homework.assigned_to != user:
            raise Http404(_("بازخورد امتحان موردنظر یافت نشد!"))

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if not hasattr(self, "base_query"):
            self.homework_feedback: HomeworkFeedback = (
                HomeworkFeedback.objects.get(
                    uuid=self.kwargs.get("uuid"),
                    homework__homework__is_delete=False,
                    is_delete=False,
                )
            )

            self.base_query = self.homework_feedback.feedbacks.filter(is_delete=False)

        return self.base_query


@login_required
def done_homework(request: HttpRequest, uuid):
    """
    Changes the status of a homework to done, using entered uuid in the url,
    if:
        1. User is authenticated
        2. The homework is assigned to user
    """

    # Saves the selected homework, using specified uuid in url,
    # If the homework is created by the user and its not delete

    homework: HomeworkCreatedFor = get_object_or_404(
        HomeworkCreatedFor,
        assigned_to=request.user,
        homework__is_delete=False,
        status__gt=1,
        uuid=uuid,
    )

    # Changes the status of homework
    # Redirects the user to previous url

    homework.status = 1
    homework.save()

    previous_url = request.META.get("HTTP_REFERER", None)

    if previous_url is None:
        return redirect(reverse("homework-list-page"))

    return redirect(previous_url)

@login_required
def in_progress_homework(request: HttpRequest, uuid):
    """
    Changes the status of a homework to in progress,
    using entered uuid in the url,
    if:
        1. User is authenticated
        2. The homework is assigned to user
    """

    # Saves the selected homework, using specified uuid in url,
    # If the homework is created by the user and its not delete

    homework: HomeworkCreatedFor = get_object_or_404(
        HomeworkCreatedFor,
        assigned_to=request.user,
        homework__is_delete=False,
        status__in=[1, 3],
        uuid=uuid,
    )

    # Changes the status of homework
    # Redirects the user to previous url or homework list page

    homework.status = 2
    homework.save()

    previous_url = request.META.get("HTTP_REFERER", None)

    if previous_url is None:
        return redirect(reverse("homework-list-page"))

    return redirect(previous_url)

@login_required
def not_done_homework(request: HttpRequest, uuid):
    """
    Changes the status of a homework to not done, using entered uuid in the url,
    if:
        1. User is authenticated
        2. The homework is assigned to user
    """

    # Saves the selected homework, using specified uuid in url,
    # If the homework is created by the user and its not delete

    homework: HomeworkCreatedFor = get_object_or_404(
        HomeworkCreatedFor,
        assigned_to=request.user,
        homework__is_delete=False,
        status__lt=3,
        uuid=uuid,
    )

    # Changes the status of homework
    # Redirects the user to previous url or homework list page

    homework.status = 3
    homework.save()

    previous_url = request.META.get("HTTP_REFERER", None)

    if previous_url is None:
        return redirect(reverse("homework-list-page"))

    return redirect(previous_url)

@login_required
def complete_homework(request: HttpRequest, uuid):
    """
    Changes the result status of a homework_result to complete,
    and finds it using entered uuid in the url,
    if:
        1. User is authenticated
        2. The homework created by user
    """

    # Saves the selected homework result, using specified uuid in url,
    # If the homework is created by the user and its not delete

    homework_result: HomeworkResult = get_object_or_404(
        HomeworkResult,
        uuid=uuid,
        is_delete=False,
        result_status__gt=1,
        homework__homework__created_by=request.user,
        homework__homework__is_delete=False,
    )

    # Changes the status of homework_result
    # Redirects the user to previous url

    homework_result.result_status = 1
    homework_result.save()

    previous_url = request.META.get("HTTP_REFERER", None)

    if previous_url is None:
        return redirect(reverse("homework-list-page"))

    return redirect(previous_url)

@login_required
def waiting_homework(request: HttpRequest, uuid):
    """
    Changes the result status of a homework_result to waitings,
    and finds it using entered uuid in the url,
    if:
        1. User is authenticated
        2. The homework created by user
    """

    # Saves the selected homework result, using specified uuid in url,
    # If the homework is created by the user and its not delete

    homework_result: HomeworkResult = get_object_or_404(
        HomeworkResult,
        uuid=uuid,
        is_delete=False,
        result_status__in=[1, 3],
        homework__homework__created_by=request.user,
        homework__homework__is_delete=False,
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
def not_complete_homework(request: HttpRequest, uuid):
    """
    Changes the result status of a homework result to not completed,
    and finds it using entered uuid in the url,
    if:
        1. User is authenticated
        2. The homework is created by user
    """

    # Saves the selected homework result, using specified uuid in url,
    # If the homework is created by the user and its not delete

    homework_result: HomeworkResult = get_object_or_404(
        HomeworkResult,
        uuid=uuid,
        is_delete=False,
        result_status__lt=3,
        homework__homework__created_by=request.user,
        homework__homework__is_delete=False,
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
def delete_homework(request: HttpRequest, type: str, uuid: str):
    """
    Delete an homework or homework result or homework feedback
    (depending of specified type in url h = homework, r = homework result, f = homework feedback)
    And Finds homework using entered uuid in the url,

    if:
        1. User is authenticated
        2. The homework is assigned to user

    """

    # Saves the user
    user = request.user

    match type:
        case "h":
            # If specified type in url is "h", Saves the specified homework (using specified uuid in url),
            # In query_set variable (If it doesn't find any homework, returns 404 page

            previous_url = None
            query_set: Homework = get_object_or_404(
                Homework,
                created_by=user,
                is_delete=False,
                uuid=uuid
            )

        case "r":
            # If specified type in url is "r", Saves the specified homework result (using specified uuid in url),
            # In query_set variable (If it doesn't find any homework, returns 404 page

            previous_url = request.META.get("HTTP_REFERER", None)
            query_set: HomeworkResult = get_object_or_404(
                HomeworkResult,
                homework__assigned_to=user,
                homework__homework__is_delete=False,
                is_delete=False,
                uuid=uuid,
            )

            feedback: QuerySet[HomeworkFeedback] = HomeworkFeedback.objects.filter(
                homework__result=query_set,
                homework__homework__is_delete=False,
                is_delete=False,
            )

            if feedback.exists():
                feedback.update(is_delete=True)

        case "f":
            # If specified type in url is "f", Saves the specified homework feedback (using specified uuid in url),
            # In query_set variable (If it doesn't find any homework, returns 404 page

            previous_url = request.META.get("HTTP_REFERER", None)
            query_set: HomeworkFeedback = get_object_or_404(
                HomeworkFeedback,
                homework__homework__created_by=user,
                homework__homework__is_delete=False,
                is_delete=False,
                uuid=uuid,
            )

        case _:
            # If specified type in url is not "e", "r" or "f" redirects the user,
            # To 404 page

            raise Http404(_("صفحه موردنظر یافت نشد."))


    # Delete the homework (Change is_delete to false)
    query_set.is_delete = True
    query_set.save()

    # If previous_url is None, it will redirect the user to the homework list page.
    # Otherwise, it will redirect the user to previous_url.

    if previous_url is None:
        return redirect(reverse("homework-list-page"))

    return redirect(previous_url)

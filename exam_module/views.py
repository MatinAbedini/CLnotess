from django.views.generic import ListView, DetailView, UpdateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator
from django.http.response import Http404
from django.http import HttpRequest
from django.db.models import Q

from account_module.models import Account
from lesson_module.models import Lesson
from class_module.models import Class
from .models import *
from .forms import *

# Create your views here.


class ExamCreateView(LoginRequiredMixin, CreateView):
    template_name = "exam_module/create-exam.html"
    success_url = reverse_lazy("exam-list-page")
    form_class = ExamForm
    model = Exam

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
                .prefetch_related("student_exams", "assigned_to")
                .only("class_name", "school_name", "uuid")
            )

        # Add classes, as options to assigned_to, field in the form

        form: ExamForm = super().get_form(form_class)
        class_choices = [(class_.uuid, class_) for class_ in self.classes]
        form.fields["assigned_to"].choices = class_choices

        return form

    def form_valid(self, form: ExamForm):
        # Saves new exam and specified classes,
        # Which are going to get assigned by the exam (saved as classes var)

        exam: Exam = form.save(commit=False)
        assigned_to_list = form.cleaned_data.get("assigned_to")
        classes = self.classes.filter(uuid__in=assigned_to_list)

        # If classes doesn't exists, returns an error for assigned_to filled
        # And makes the form invalid

        if not classes.exists():
            form = self.get_form
            form.add_error("assigned_to", ".کلاس هایی که انتخاب کرده اید وجود ندارد")

            return super().form_invalid(form)

        # Sets created by of the exam to the user,
        # Assigns exam to specified classes,
        # And redirects the user to the default success url page (exam list page)

        exam.created_by = self.request.user
        exam.save()
        exam.assign_exam(classes)

        return super().form_valid(form)


class ExamUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "exam_module/edit-exam.html"
    success_url = reverse_lazy("exam-list-page")
    form_class = ExamForm
    model = Exam
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def get_queryset(self):
        # If the queryset isn't cached, it will save the queryset and cache it
        # Otherwise, it will return cached values

        if not hasattr(self, "base_query"):
            self.base_query = (
                Exam.objects.filter(
                    uuid=self.kwargs.get("uuid"),
                    created_by=self.request.user,
                    is_delete=False,
                )
            )

        return self.base_query

    def get_form(self, form_class=None):
        # Add classes, as options to assigned_to, field in the form

        self.base_query = self.base_query.first()
        form: ExamForm = super().get_form(form_class)
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
                .prefetch_related("student_exams", "assigned_to")
                .only("class_name", "school_name", "uuid")
            )

        initial = super().get_initial()
        classes = (self.classes.filter(assigned_exams=self.get_queryset()))
        initial["assigned_to"] = [class_.uuid for class_ in classes]

        return initial

    def form_valid(self, form: ExamForm):
        # Saves modified exam, base exam (not modified version)
        # and specified classes, Which are going to get assigned by the exam (saved as classes var)

        new_exam: Exam = form.save(commit=False)
        old_exam: Exam = self.get_queryset()
        assigned_to_list = form.cleaned_data.get("assigned_to")
        classes = self.classes.filter(uuid__in=assigned_to_list)

        # If classes doesn't exists, returns an error for assigned_to filled
        # And makes the form invalid

        if not classes.exists():
            form = self.get_form
            form.add_error("assigned_to", ".کلاس هایی که انتخاب کرده اید وجود ندارد")

            return super().form_invalid(form)

        # Saves added and removed classes from base exam (not modified exam),
        # With finding differences on assigned classes of both exams (modified and not modified)
        # Assigns new exams and unassigns removed exams from exam

        new_exam_classes = set(
            new_exam.assigned_class.all().values_list("id", flat=True)
        )
        old_exam_classes = set(
            old_exam.assigned_class.all().values_list("id", flat=True)
        )

        added_classes = [
            new_exam_class

            for new_exam_class in new_exam_classes
            if not new_exam_class in old_exam_classes
        ]

        removed_classes = [
            old_exam_class

            for old_exam_class in old_exam_classes
            if not old_exam_class in new_exam_classes
        ]

        new_exam.assign_exam(added_classes)
        new_exam.unassign_exam(removed_classes)

        # Modifies every other modified fields, save Changes,
        # And at the end if the form is valid redirects the user to the default success url page
        # (exam list page)

        return super().form_valid(form)


class ExamListView(LoginRequiredMixin, ListView):
    template_name = "exam_module/exams-list.html"
    context_object_name = "exams"
    model = Exam
    ordering = "status"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        # Save default contexts, difficulty and lessons
        context = super().get_context_data(**kwargs)
        lessons = Lesson.objects.all().only("name")

        # Save status, difficulty and lesson which are going to get filtered
        # And save lessons, and those filters in the context

        context["status_filter"] = self.request.GET.get("status", "")
        context["difficulty_filter"] = self.request.GET.get("difficulty", "")
        context["lesson_filter"] = self.request.GET.get("lesson", "")
        context["lessons"] = [lesson.name for lesson in lessons]

        return context

    def get_queryset(self):
        # If the queryset isn't cached, it will save the queryset and cache it
        # Otherwise, it will return cached values

        if not hasattr(self, "base_query"):
            self.base_query = (
                ExamCreatedFor.objects.filter(
                    assigned_to=self.request.user,
                    exam__is_delete=False,
                )
            )

        difficulty_filter: str = self.request.GET.get("difficulty", "")
        status_filter: str = self.request.GET.get("status", "")
        lesson_filter: str = self.request.GET.get("lesson", "")

        # Filter exams by difficulty, status and lesson fields,
        # If user has filter exams using them

        if difficulty_filter != "":
            difficulty_filter = list(map(int, difficulty_filter.split(",")))
            self.base_query = self.base_query.filter(exam__difficulty__in=difficulty_filter)

        if status_filter != "":
            status_filter = list(map(int, status_filter.split(",")))
            self.base_query = self.base_query.filter(exam__status__in=status_filter)

        if lesson_filter != "":
            lesson_filter = lesson_filter.split(",")
            self.base_query = self.base_query.filter(exam__lesson__name__in=lesson_filter)

        return self.base_query


class ExamDetailView(LoginRequiredMixin, DetailView):
    template_name = "exam_module/exam.html"
    context_object_name = "exam"
    model = ExamCreatedFor
    slug_url_kwarg = "uuid"
    slug_field = "uuid"

    def get_queryset(self):
        # If the queryset isn't cached, it will save the queryset and cache it
        # Otherwise, it will return cached values

        if not hasattr(self, "base_query"):
            self.base_query = (
                ExamCreatedFor.objects.filter(
                    uuid=self.kwargs.get("uuid"),
                    assigned_to=self.request.user,
                    exam__is_delete=False,
                )
                .select_related("exam", "result", "feedback")
            )

        return self.base_query


class ExamResultCreateView(LoginRequiredMixin, CreateView):
    template_name = "exam_module/create-exam-result.html"
    success_url = reverse_lazy("exam-list-page")
    form_class = ExamResultForm
    model = ExamResult

    def dispatch(self, request, *args, **kwargs):
        self.get_form()
        if not self.students.exists():
            raise Http404(_("نتیجه امتحان برای تمامی دانش آموزان ثبت شده است."))

        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        # Saves the for for modifying it
        form: ExamResultForm = super().get_form(form_class)

        # If the exam (The exam which is for the new result),
        # And students (Students Which are assigned to exam) are not cached (saved)
        # Finds and Saves them (Exam: Using specified uuid in url, Students: Assigned users to the exam)

        if not hasattr(self, "exam"):
            self.exam = get_object_or_404(Exam, uuid=self.kwargs.get("uuid"), is_delete=False)

        if not hasattr(self, "students"):
            self.exam_created_for: QuerySet[ExamCreatedFor] = (
                self.exam.assigned_users.filter(
                    Q(result=None) | Q(result__is_delete=True)
                )
            )

            students_id = self.exam_created_for.values_list("assigned_to", flat=True)
            self.students: QuerySet[Account] = Account.objects.filter(id__in=students_id)

        # Saves students as options (User Active Code / User Full Name)
        # Sets students as option for the student field in the form
        # Returns the updated form

        students_options = [
            (student.username, student.get_full_name)
            for student in self.students
        ]

        form.fields["student"].choices = students_options

        return form

    def form_valid(self, form):
        # Save ExamCreatedFor (Specified Exam),
        # Using entered uuid in the url, or selected Exam in the form

        exam_uuid = self.kwargs.get("uuid")
        exam: ExamCreatedFor = (
            ExamCreatedFor.objects.get(
                exam__uuid=exam_uuid,
                assigned_to__username=form.cleaned_data.get("student"),
                exam__is_delete=False
            )
        )

        # Save assigned files to the result as a list
        # Save new Exam_result, and set it as feedback of ExamCreatedFor

        files = self.request.FILES.getlist("files")
        exam_result = form.save()
        exam.result = exam_result
        exam.save()

        # Upload and save, Exam_result files in server

        exam_result_files = [
            ExamResultFile(
                exam=exam_result,
                file=file
            )
            for file in files
        ]

        ExamResultFile.objects.bulk_create(exam_result_files)

        return super().form_valid(form)


class ExamResultUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "exam_module/edit-exam-result.html"
    success_url = reverse_lazy("exam-list-page")
    context_object_name = "exam_result"
    form_class = ExamResultForm
    model = ExamResult
    slug_url_kwarg = "uuid"
    slug_field = "exam__uuid"

    def get_form_kwargs(self):
        # Makes files field optional
        kwargs = super().get_form_kwargs()
        kwargs["files_required"] = False

        return kwargs

    def get_form(self, form_class=None):
        # Saves the for for modifying it
        form: ExamResultForm = super().get_form(form_class)

        # If the exam (The exam which is for the new result),
        # And students (Students Which are assigned to exam) are not cached (saved)
        # Finds and Saves them (Exam: Using specified uuid in url, Students: Assigned users to the exam)

        if not hasattr(self, "exam"):
            self.exam = self.base_query.first().exam.exam

        if not hasattr(self, "students"):
            self.exam_created_for: QuerySet[ExamCreatedFor] = self.exam.assigned_users.all()
            students_id = self.exam_created_for.values_list("assigned_to", flat=True)
            self.students: QuerySet[Account] = Account.objects.filter(id__in=students_id)

        # Saves students as options (User Active Code / User Full Name)
        # Sets students as option for the student field in the form
        # Returns the updated form

        students_options = [
            (student.username, student.get_full_name)
            for student in self.students
        ]

        form.fields["student"].choices = students_options

        return form

    def form_valid(self, form):
        exam_result = form.save()
        new_files = self.request.FILES.getlist("files")
        old_files = exam_result.results.all()
        old_files.update(is_delete=True)

        # Upload and save, Exam_result files in server

        exam_result_files = [
            ExamResultFile(
                exam=exam_result,
                file=file
            )
            for file in new_files
        ]

        ExamResultFile.objects.bulk_create(exam_result_files)

        return super().form_valid(form)

    def get_queryset(self):
        # If the queryset isn't cached, it will save the queryset and cache it
        # Otherwise, it will return cached values

        if not hasattr(self, "base_query"):
            self.base_query = super().get_queryset()
            self.base_query = (
                self.base_query.filter(
                    exam__exam__created_by=self.request.user,
                    exam__exam__is_delete=False,
                    is_delete=False,
                )
            )

        return self.base_query


class ExamResultFileListView(LoginRequiredMixin, ListView):
    template_name = "exam_module/exam-result-file-list.html"
    context_object_name = "files"
    model = ExamResultFile

    def dispatch(self, request, *args, **kwargs):
        # Runs get_queryset function, so self.exam_result get created by the function
        # Saves the user

        self.get_queryset()
        user = self.request.user

        # If exam if self.exam_result is not created by user or assigned to user,
        # It will raise 404 page

        if self.exam_result.exam.exam.created_by != user and self.exam_result.exam.assigned_to != user:
            raise Http404(_("نتیجه امتحان موردنظر یافت نشد!"))

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # If the queryset isn't cached, it will save the queryset and cache it
        # Otherwise, it will return cached values

        if not hasattr(self, "base_query"):
            self.exam_result: ExamResult = (
                ExamResult.objects.get(
                    uuid=self.kwargs.get("uuid"),
                    exam__exam__is_delete=False,
                    is_delete=False,
                )
            )

            self.base_query = self.exam_result.results.filter(is_delete=False)

        return self.base_query


class ExamFeedbackDetailView(LoginRequiredMixin, DetailView):
    template_name = "exam_module/exam-feedback.html"
    context_object_name = "exam"
    model = ExamCreatedFor
    slug_url_kwarg = "uuid"
    slug_field = "uuid"

    def get_queryset(self):
        # If the queryset isn't cached, it will save the queryset and cache it
        # Otherwise, it will return cached values

        if not hasattr(self, "base_query"):
            self.base_query = (
                Exam.objects.filter(
                    uuid=self.kwargs.get("uuid"),
                    created_by=self.request.user,
                    is_delete=False,
                )
            )

        return self.base_query

    def get_context_data(self, **kwargs):
        # Save default contexts, base_query (specified ExamCreatedFor) and page
        exam = self.get_queryset().first()
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get("page", 1)

        # Convert the page number from str to int
        # If can't convert it, because page number is not a number set page first page

        try:
            page = int(page)
        except ValueError:
            page = 1

        # Saves every other ExamCreatedFor of that exam,
        # If the exam has result
        exams: QuerySet[ExamCreatedFor] = (
            ExamCreatedFor.objects.filter(
                exam=exam,
                result__is_delete=False
            )
            .exclude(result=None)
            .order_by("modify_date")
            .select_related("exam", "feedback", "result")
        )

        # If at least one result is submitted
        # Paginate exams (One in each page)
        # Send result and feedback of that page with page_obj
        # Else Send Null for result and feedback

        if not exams.exists():
            context["result"] = None
            context["feedback"] = None

            return context

        paginator = Paginator(exams, 1)
        page_obj = paginator.page(page)
        exam = page_obj.object_list[0]

        context["result"] = exam.result
        context["feedback"] = exam.feedback
        context["page_obj"] = page_obj

        return context


class ExamFeedbackCreateView(LoginRequiredMixin, CreateView):
    template_name = "exam_module/create-exam-feedback.html"
    success_url = reverse_lazy("exam-list-page")
    form_class = ExamFeedbackForm
    model = ExamFeedback

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(self, "exam"):
            # Save examCreatedFor (Specified exam),
            # Using entered uuid in the url, or selected exam in the form

            self.exam: ExamCreatedFor = (
                ExamCreatedFor.objects.get(
                    uuid=self.kwargs.get("uuid"),
                    assigned_to__username=self.request.user,
                    exam__is_delete=False
                )
            )

        if self.exam.feedback is not None:
            raise Http404(_("بازخورد امتحان قبلا ثبت شده است."))

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Save assigned files to the feedback as a list
        # Save new exam_feedback, and set it as feedback of examCreatedFor

        files = self.request.FILES.getlist("files")
        exam_feedback = form.save()
        self.exam.feedback = exam_feedback
        self.exam.save()

        # Upload and save, exam_feedback files in server

        exam_feedback_files = [
            ExamFeedbackFile(
                exam=exam_feedback,
                file=file
            )
            for file in files
        ]

        ExamFeedbackFile.objects.bulk_create(exam_feedback_files)

        return super().form_valid(form)


class ExamFeedbackUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "exam_module/edit-exam-feedback.html"
    success_url = reverse_lazy("exam-list-page")
    context_object_name = "exam_feedback"
    form_class = ExamFeedbackForm
    model = ExamFeedback
    slug_url_kwarg = "uuid"
    slug_field = "exam__uuid"

    def get_form_kwargs(self):
        # Makes files field optional
        kwargs = super().get_form_kwargs()
        kwargs["files_required"] = False

        return kwargs

    def form_valid(self, form):
        exam_feedback = form.save()
        new_files = self.request.FILES.getlist("files")
        old_files = exam_feedback.feedbacks.all()
        old_files.update(is_delete=True)

        # Upload and save, Exam_feedback files in server

        exam_feedback_files = [
            ExamFeedbackFile(
                exam=exam_feedback,
                file=file
            )
            for file in new_files
        ]

        ExamFeedbackFile.objects.bulk_create(exam_feedback_files)

        return super().form_valid(form)

    def get_queryset(self):
        # If the queryset isn't cached, it will save the queryset and cache it
        # Otherwise, it will return cached values

        if not hasattr(self, "base_query"):
            self.base_query = super().get_queryset()
            self.base_query = (
                ExamFeedback.objects.filter(
                    exam__assigned_to=self.request.user,
                    exam__exam__is_delete=False,
                    is_delete=False,
                )
            )

        return self.base_query


class ExamFeedbackFileListView(LoginRequiredMixin, ListView):
    template_name = "exam_module/exam-feedback-file-list.html"
    context_object_name = "files"
    model = ExamFeedbackFile

    def dispatch(self, request, *args, **kwargs):
        # Runs get_queryset function, so self.exam_feedback get created by the function
        # Saves the user

        self.get_queryset()
        user = self.request.user

        # If exam if self.exam_feedback is not created by user or assigned to user,
        # It will raise 404 page

        if self.exam_feedback.exam.exam.created_by != user and self.exam_feedback.exam.assigned_to != user:
            raise Http404(_("بازخورد امتحان موردنظر یافت نشد!"))

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # If the queryset isn't cached, it will save the queryset and cache it
        # Otherwise, it will return cached values

        if not hasattr(self, "base_query"):
            self.exam_feedback: ExamFeedback = (
                ExamFeedback.objects.get(
                    uuid=self.kwargs.get("uuid"),
                    exam__exam__is_delete=False,
                    is_delete=False,
                )
            )

            self.base_query = ExamFeedbackFile.objects.filter(
                exam=self.exam_feedback,
                is_delete=False,
            )

        return self.base_query


@login_required
def done_exam(request: HttpRequest, uuid):
    """
    Changes the status of an exam to done
    And finds exam using entered uuid in the url,
    if:
        1. User is authenticated
        2. The exam is assigned to user
    """

    # Saves the selected exam, using specified uuid in url,
    # If the exam is created by the user and its not delete

    exam: Exam = get_object_or_404(
        Exam,
        uuid=uuid,
        status=2,
        created_by=request.user,
        is_delete=False,
    )


    # Changes the status of exam
    # Redirects the user to previous url

    exam.status = 1
    exam.save()

    previous_url = request.META.get("HTTP_REFERER", None)

    if previous_url is None:
        return redirect(reverse("exam-list-page"))

    return redirect(previous_url)

@login_required
def not_done_exam(request: HttpRequest, uuid):
    """
    Changes the status of an exam to not done
    And finds exam using entered uuid in the url,
    if:
        1. User is authenticated
        2. The exam is assigned to user
    """

    # Saves the selected exam, using specified uuid in url,
    # If the exam is created by the user and its not delete

    exam: Exam = get_object_or_404(
        Exam,
        uuid=uuid,
        status=1,
        created_by=request.user,
        is_delete=False,
    )

    # Changes the status of exam
    # Redirects the user to previous url or exam list page

    exam.status = 2
    exam.save()

    previous_url = request.META.get("HTTP_REFERER", None)

    if previous_url is None:
        return redirect(reverse("exam-list-page"))

    return redirect(previous_url)

@login_required
def pass_exam(request: HttpRequest, uuid):
    """
    Changes the result status of a exam_result to passes,
    and finds it using entered uuid in the url,
    if:
        1. User is authenticated
        2. The exam created by user
    """

    # Saves the selected exam result, using specified uuid in url,
    # If the exam is created by the user and its not delete

    exam_result: ExamResult = get_object_or_404(
        ExamResult,
        uuid=uuid,
        exam__exam__created_by=request.user,
        exam__exam__is_delete=False,
        is_delete=False,
        result=2,
    )

    # Changes the status of exam_result
    # Redirects the user to previous url

    exam_result.result = 1
    exam_result.save()

    previous_url = request.META.get("HTTP_REFERER", None)

    if previous_url is None:
        return redirect(reverse("exam-list-page"))

    return redirect(previous_url)

@login_required
def fail_exam(request: HttpRequest, uuid):
    """
    Changes the result status of a exam_result to failed,
    and finds it using entered uuid in the url,
    if:
        1. User is authenticated
        2. The exam created by user
    """

    # Saves the selected exam result, using specified uuid in url,
    # If the exam is created by the user and its not delete

    exam_result: ExamResult = get_object_or_404(
        ExamResult,
        uuid=uuid,
        is_delete=False,
        exam__exam__is_delete=False,
        exam__exam__created_by=request.user,
        result=1,
    )

    # Changes the status of the exam result
    # Redirects the user to previous url

    exam_result.result = 2
    exam_result.save()
    previous_url = request.META.get("HTTP_REFERER", None)

    if previous_url is None:
        return redirect(reverse("exam-list-page"))

    return redirect(previous_url)

@login_required
def delete_exam(request: HttpRequest, type: str, uuid: str):
    """
    Delete an exam or exam result or exam feedback
    (depending of specified type in url e = exam, r = exam result, f = exam feedback)
    And Finds exam using entered uuid in the url,

    if:
        1. User is authenticated
        2. The exam is assigned to user

    """

    # Saves the user and pervious url (The url which user is redirected from)
    user = request.user

    match type:
        case "e":
            # If specified type in url is "e", Saves the specified exam (using specified uuid in url),
            # In query_set variable (If it doesn't find any exam, returns 404 page

            previous_url = None
            query_set: Exam = get_object_or_404(
                Exam,
                created_by=user,
                is_delete=False,
                uuid=uuid
            )

        case "r":
            # If specified type in url is "r", Saves the specified exam result (using specified uuid in url),
            # In query_set variable (If it doesn't find any exam, returns 404 page

            previous_url = request.META.get("HTTP_REFERER", None)
            query_set: ExamResult = get_object_or_404(
                ExamResult,
                exam__exam__created_by=user,
                exam__exam__is_delete=False,
                is_delete=False,
                uuid=uuid,
            )

            feedback: QuerySet[ExamFeedback] = ExamFeedback.objects.filter(
                exam__result=query_set,
                exam__exam__is_delete=False,
                is_delete=False,
            )

            if feedback.exists():
                feedback.update(is_delete=True)

        case "f":
            # If specified type in url is "f", Saves the specified exam feedback (using specified uuid in url),
            # In query_set variable (If it doesn't find any exam, returns 404 page

            previous_url = request.META.get("HTTP_REFERER", None)
            query_set: ExamFeedback = get_object_or_404(
                ExamFeedback,
                exam__assigned_to=user,
                exam__exam__is_delete=False,
                is_delete=False,
                uuid=uuid,
            )

        case _:
            # If specified type in url is not "e", "r" or "f" redirects the user,
            # To 404 page

            raise Http404(_("صفحه موردنظر یافت نشد."))


    # Deletes the exam (Change is_delete to false)
    query_set.is_delete = True
    query_set.save()

    # If previous_url is None, it will redirect the user to the exam list page.
    # Otherwise, it will redirect the user to previous_url.

    if previous_url is None:
        return redirect(reverse("exam-list-page"))

    return redirect(previous_url)

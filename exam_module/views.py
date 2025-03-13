from django.views.generic import ListView, DetailView, UpdateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.functions import Concat
from django.db.models import Q, F, Value

from account_module.models import Account
from lesson_module.models import Lesson
from class_module.models import Class
from .forms import ExamForm, ExamResultForm
from .models import Exam, ExamResult

# Create your views here.


class ExamCreateView(LoginRequiredMixin, CreateView):
    model = Exam
    form_class = ExamForm
    template_name = "exam_module/create-exam.html"
    success_url = reverse_lazy("exam-list-page")

    def get_form(self, form_class=None):
        user = self.request.user
        classes = (
            Class.objects.filter(
                Q(teachers__teacher=user) | Q(created_by=user),
                is_delete=False
            ).only("class_name", "school_name", "id")
        )

        form: ExamForm = super().get_form(form_class)
        class_choices = [(class_.id, class_) for class_ in classes]
        form.fields["assigned_to"].choices = class_choices

        return form

    def form_valid(self, form: ExamForm):
        super().form_valid(form)

        assigned_to = form.cleaned_data.get("assigned_to")
        new_exam: Exam = form.save(commit=False)
        new_exam.created_by = self.request.user
        new_exam.assigned_to.add(*assigned_to)
        new_exam.save()

        return super().form_valid(form)


class ExamUpdateView(LoginRequiredMixin, UpdateView):
    model = Exam
    form_class = ExamForm
    template_name = "exam_module/update-exam.html"
    success_url = reverse_lazy("exam-list-page")
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def get_form(self, form_class=None):
        classes = (
            Class.objects.filter(
                teachers__teacher=self.request.user,
                is_delete=False
            ).only("class_name", "school_name", "id")
        )

        form: ExamForm = super().get_form(form_class)
        class_choices = [(class_.id, class_.__str__) for class_ in classes]
        form.fields["assigned_to"].choices = class_choices

        return form

    def get_queryset(self):
        base_query = super().get_queryset()
        base_query = base_query.filter(
            created_by=self.request.user,
            is_delete=False
        )

        return base_query


class ExamListView(LoginRequiredMixin, ListView):
    template_name = "exam_module/exams-list.html"
    context_object_name = "exams"
    ordering = "status"
    model = Exam
    paginate_by = 10

    def get_context_data(self, **kwargs):
        # Save default contexts, difficulty, lessons and classes
        context = super().get_context_data(**kwargs)
        lessons = Lesson.objects.all().only("name")
        exams = self.get_queryset()

        classes = set(
            class_
            for exam in exams
            for class_ in exam.assigned_to.all().annotate(str=Concat(F("school_name"), Value(" "), F("class_name")))
        )

        # Save status, difficulty, lesson and classes which are going to get filtered
        # And save lessons, classes and those filters in the context

        context["status_filter"] = self.request.GET.get("status", "")
        context["difficulty_filter"] = self.request.GET.get("difficulty", "")
        context["lesson_filter"] = self.request.GET.get("lesson", "")
        context["class_filter"] = self.request.GET.get("class_", "")
        context["lessons"] = [lesson.name for lesson in lessons]
        context["classes"] = list(classes)

        return context

    def get_queryset(self):
        # If the queryset isn't cached, save the queryset and cache it
        # Else returns the cached values

        if not hasattr(self, "base_query"):
            # Save user and used filters
            # Filters assigned and not deleted exams

            user = self.request.user
            difficulty_filter: str = self.request.GET.get("difficulty", "")
            status_filter: str = self.request.GET.get("status", "")
            lesson_filter: str = self.request.GET.get("lesson", "")
            class_filter: str = self.request.GET.get("class_", "")

            self.base_query = Exam.objects.filter(
                assigned_to__assigned_to=user,
                is_delete=False
            )

            # Filter exams by difficulty, status, lesson and class field,
            # If user has filter exams using them

            if difficulty_filter != "":
                difficulty_filter = list(map(int, difficulty_filter.split(",")))
                self.base_query = self.base_query.filter(difficulty__in=difficulty_filter)

            if status_filter != "":
                status_filter = list(map(int, status_filter.split(",")))
                self.base_query = self.base_query.filter(status__in=status_filter)

            if lesson_filter != "":
                lesson_filter = lesson_filter.split(",")
                self.base_query = self.base_query.filter(lesson__name__in=lesson_filter)

            if class_filter != "":
                class_filter = class_filter.split(",")
                self.self.base_query = self.self.base_query.filter(class__str__in=class_filter)

            return self.base_query

        return self.base_query


class ExamDetailView(LoginRequiredMixin, DetailView):
    model = Exam
    template_name = "exam_module/exam.html"
    context_object_name = "exam"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def get_queryset(self):
        # If the queryset isn't cached, save the queryset and cache it
        # Else returns the cached values

        if not hasattr(self, "base_query"):
            self.base_query = (
                Exam.objects.filter(
                    uuid=self.kwargs.get("uuid"),
                    assigned_to__assigned_to=self.request.user,
                    is_delete=False
                )
                .select_related("")
            )

            return self.base_query

        return self.base_query


class ExamResultCreateView(LoginRequiredMixin, CreateView):
    form_class = ExamResultForm
    template_name =  "exam_module/create-exam-result.html"
    success_url = reverse_lazy("index-page")

    def get_form(self, form_class=None):
        user = self.request.user
        exams = (
            Exam.objects.filter(
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
        exam_choices = [(exam.uuid, exam.title) for exam in exams]
        student_choices = [
            (student.active_code, student.username)
            for student in students
        ]

        form.fields["exam"].choices = exam_choices
        form.fields["student"].choices = student_choices

        return form

    def form_valid(self, form):
        exam_result = form.save(commit=False)
        exam_result.exam = (
            Exam.objects.get(
                uuid=form.cleaned_data.get("exam"),
                is_delete=False
            )
        )
        exam_result.student = (
            Account.objects.get(
                active_code=form.cleaned_data.get("student"),
                is_active=True
            )
        )

        return super().form_valid(form)


class ExamResultUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "exam_module/edit-exam-result.html"
    success_url = reverse_lazy("index-page")
    context_object_name = "exam_result"
    form_class = ExamResultForm
    model = ExamResult
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def get_queryset(self):
        base_query = super().get_queryset()
        base_query = base_query.filter(
            is_delete=False
        )

        return base_query

    def get_form(self, form_class=None):
        user = self.request.user

        exams = (
            Exam.objects.filter(
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
        exam_choices = [(exam.uuid, exam.title) for exam in exams]
        student_choices = [
            (student.active_code, student.username)
            for student in students
        ]

        form.fields["exam"].choices = exam_choices
        form.fields["student"].choices = student_choices

        return form

    def form_valid(self, form):
        exam_result = form.save(commit=False)
        exam_result.exam = (
            Exam.objects.get(
                uuid=form.cleaned_data.get("exam"),
                is_delete=False
            )
        )
        exam_result.student = (
            Account.objects.get(
                active_code=form.cleaned_data.get("student"),
                is_active=True
            )
        )

        return super().form_valid(form)


class ExamResultDetailView(LoginRequiredMixin, DetailView):
    model = ExamResult
    template_name = "exam_module/exam-result.html"
    context_object_name = "exam_result"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def get_queryset(self):
        base_query = super().get_queryset()
        base_query = base_query.filter(
            is_delete=False
        )

        return base_query


@login_required
def done_exam(request, uuid):
    """
    Changes the status of an exam to done
    And finds exam using entered uuid in the url,
    if:
        1. User is authenticated
        2. The exam is assigned to user
    """

    # Save the user
    # Save exam, if its assigned to user

    user = request.user
    exam: Exam = get_object_or_404(
        Exam.objects.filter(
            assigned_to__assigned_to=user,
            is_delete=False,
            uuid=uuid
        )
        .exclude(status=1)
        .only("status")
    )

    # Change the status of exam
    # Redirect the user to previous url

    exam.status = 1
    exam.save()

    previous_url = request.META.get("HTTP_REFERER", None)

    if previous_url is None:
        return redirect(reverse("exam-list-page"))

    return redirect(previous_url)

@login_required
def not_done_exam(request, uuid):
    """
    Changes the status of an exam to not done
    And finds exam using entered uuid in the url,
    if:
        1. User is authenticated
        2. The exam is assigned to user
    """

    # Save the user
    # Save exam, if its assigned to user

    user = request.user
    exam: Exam = get_object_or_404(
        Exam.objects.filter(
            assigned_to__assigned_to=user,
            is_delete=False,
            uuid=uuid
        )
        .exclude(status=2)
        .only("status")
    )

    # Change the status of exam
    # Redirect the user to previous url or exam list page

    exam.status = 2
    exam.save()

    previous_url = request.META.get("HTTP_REFERER", None)

    if previous_url is None:
        return redirect(reverse("exam-list-page"))

    return redirect(previous_url)

@login_required
def delete_exam(request, uuid):
    """
    Delete an exam (Change is_delete to false),
    And Finds exam using entered uuid in the url,
    if:
        1. User is authenticated
        2. The exam is assigned to user
    """

    # Save the user
    # Save exam, if its assigned to user

    user = request.user
    exam: Exam = get_object_or_404(
        Exam.objects.filter(
            created_by=user,
            is_delete=False,
            uuid=uuid
        )
        .only("is_delete")
    )

    # Delete the exam (Change is_delete to false)
    # Redirect the user to previous url

    exam.is_delete = True
    exam.save()

    return redirect(reverse("exam-list-page"))

from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView
from account_module.models import Account
from class_module.models import Class
from django.db.models import Q
from django.http import HttpRequest
from .forms import ExamForm, ExamResultForm
from .models import Exam, ExamResult

# Create your views here.


class ExamCreateView(CreateView):
    model = Exam
    form_class = ExamForm
    template_name = "exam_module/create-exam.html"
    success_url = reverse_lazy("exam-list-page")

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


class ExamUpdateView(UpdateView):
    model = Exam
    form_class = ExamForm
    template_name = "exam_module/update-exam.html"
    success_url = reverse_lazy("exam-list-page")
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login-page"))

        return  super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        classes = (
            Class.objects.filter(
                teachers__teacher=self.request.user,
                is_active=True,
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
            is_active=True,
            is_delete=False
        )

        return base_query


class ExamListView(ListView):
    template_name = "exam_module/exams-list.html"
    context_object_name = "exams"
    model = Exam
    ordering = "status"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login-page"))

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        base_query = Exam.objects.filter(
            assigned_to__assigned_to=user,
            is_active=True,
            is_delete=False
        )

        return base_query


class ExamDetailView(DetailView):
    model = Exam
    template_name = "exam_module/exam.html"
    context_object_name = "exam"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login-page"))

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        base_query = super().get_queryset()
        base_query = base_query.filter(
            assigned_to__assigned_to=user,
            is_active=True,
            is_delete=False
        )

        return base_query


class ExamResultCreateView(CreateView):
    form_class = ExamResultForm
    template_name =  "exam_module/create-exam-result.html"
    success_url = reverse_lazy("index-page")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login-page"))

        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        user = self.request.user
        exams = (
            Exam.objects.filter(
                created_by=user,
                is_active=True,
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
                is_active=True,
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


class ExamResultUpdateView(UpdateView):
    model = ExamResult
    form_class = ExamResultForm
    template_name = "exam_module/edit-exam-result.html"
    success_url = reverse_lazy("index-page")
    context_object_name = "exam_result"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"


    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login-page"))

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        base_query = super().get_queryset()
        base_query = base_query.filter(
            is_active=True,
            is_delete=False
        )

        return base_query

    def get_form(self, form_class=None):
        user = self.request.user

        exams = (
            Exam.objects.filter(
                created_by=user,
                is_active=True,
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
                is_active=True,
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


class ExamResultDetailView(DetailView):
    model = ExamResult
    template_name = "exam_module/exam-result.html"
    context_object_name = "exam_result"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login-page"))

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        base_query = super().get_queryset()
        base_query = base_query.filter(
            is_active=True,
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
            is_active=True,
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
            is_active=True,
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
            is_active=True,
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

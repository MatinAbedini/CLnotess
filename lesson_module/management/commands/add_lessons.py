from django.core.management.base import BaseCommand
from lesson_module.models import Lesson

class Command(BaseCommand):
    help = "Adds default lessons to the database"

    def handle(self, *args, **options):
        lessons_names = (
            "دیگر",
            "ریاضی",
            "علوم",
            "عربی",
            "انگلیسی",
            "فارسی",
            "نگارش",
            "قرآن",
            "دینی",
            "هنر",
            "مطالعات اجتماعی",
            "تفکر و پژوهش",
            "کار و فناوری",
            "تفکر و سبک زندگی",
            "آمادگی دفاعی",
            "فرهنگ و هنر",
        )

        lessons = [
            Lesson(name=lesson_name)
            for lesson_name in lessons_names
        ]

        Lesson.objects.bulk_create(lessons)
        self.stdout.write(self.style.SUCCESS(f"default lessons added successfully! ({len(lessons_names)} lessons added)"))

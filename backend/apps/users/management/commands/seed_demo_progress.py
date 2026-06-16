from __future__ import annotations

from datetime import datetime, time, timedelta
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from PIL import Image

from apps.attendance.models import AttendanceRecord
from apps.gamification.models import PointTransaction, UserProgress
from apps.gamification.services import PointsService
from apps.gamification.strategies import AttendancePointsStrategy
from apps.study.models import StudySession
from apps.users.models import User


class Command(BaseCommand):
    help = (
        "Cria ou recria um usuario demo com 20 dias consecutivos de progresso para "
        "visualizar o grafico."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            default="demo.grafico@schoolcircle.local",
            help="Email do usuario demo.",
        )
        parser.add_argument(
            "--password",
            default="SchoolCircle123!",
            help="Senha do usuario demo.",
        )
        parser.add_argument(
            "--name",
            default="Demo Grafico",
            help="Nome completo do usuario demo.",
        )
        parser.add_argument(
            "--days",
            type=int,
            default=20,
            help="Quantidade de dias consecutivos a gerar.",
        )

    def handle(self, *args, **options):
        email = options["email"].strip().lower()
        password = options["password"]
        full_name = options["name"].strip()
        days = options["days"]

        if days < 1:
            raise ValueError("A quantidade de dias deve ser maior que zero.")

        user = self._get_or_create_demo_user(
            email=email, password=password, full_name=full_name
        )

        with transaction.atomic():
            self._clear_demo_data(user)
            self._seed_progress(user=user, days=days)

        progress = UserProgress.objects.get(user=user)

        self.stdout.write(
            self.style.SUCCESS(
                "Usuario demo pronto: {email} / {password}".format(
                    email=email, password=password
                )
            )
        )
        self.stdout.write(
            f"Streak atual: {progress.current_streak} | "
            f"Maior streak: {progress.longest_streak} | "
            f"Total de pontos: {progress.total_points}"
        )

    def _get_or_create_demo_user(
        self, email: str, password: str, full_name: str
    ) -> User:
        user, _ = User.objects.get_or_create(
            email=email,
            defaults={"full_name": full_name, "is_active": True},
        )
        user.full_name = full_name
        user.is_active = True
        user.set_password(password)
        user.save(update_fields=["full_name", "is_active", "password"])
        return user

    def _clear_demo_data(self, user: User) -> None:
        PointTransaction.objects.filter(user=user).delete()
        AttendanceRecord.objects.filter(user=user).delete()
        StudySession.objects.filter(user=user).delete()
        UserProgress.objects.filter(user=user).delete()

    def _seed_progress(self, user: User, days: int) -> None:
        start_date = timezone.localdate() - timedelta(days=days - 1)

        for index in range(days):
            activity_date = start_date + timedelta(days=index)
            points = [5, 10, 15, 20][index % 4]
            attendance = self._create_attendance(
                user=user, activity_date=activity_date, points=points, index=index
            )
            transaction = PointsService.grant_points(
                user=user,
                activity=attendance,
                strategy=AttendancePointsStrategy(),
            )
            if transaction is not None:
                PointTransaction.objects.filter(id=transaction.id).update(
                    created_at=timezone.make_aware(
                        datetime.combine(activity_date, time(12, 0))
                    )
                )

    def _create_attendance(
        self, user: User, activity_date, points: int, index: int
    ) -> AttendanceRecord:
        image_file = self._build_demo_image(
            f"demo_attendance_{index + 1}.jpg", color=self._color_for_index(index)
        )
        attendance = AttendanceRecord.objects.create(
            user=user,
            class_date=activity_date,
            period=AttendanceRecord.Period.MORNING,
            photo_url=image_file,
            is_valid=True,
            points_granted=points,
        )
        return attendance

    @staticmethod
    def _color_for_index(index: int) -> tuple[int, int, int]:
        palette = [
            (239, 68, 68),
            (245, 158, 11),
            (34, 197, 94),
            (59, 130, 246),
        ]
        return palette[index % len(palette)]

    @staticmethod
    def _build_demo_image(name: str, color: tuple[int, int, int]) -> ContentFile:
        image = Image.new("RGB", (800, 600), color=color)
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        return ContentFile(buffer.getvalue(), name=name)

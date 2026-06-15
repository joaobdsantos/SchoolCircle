from django.db import transaction

from apps.gamification.models import PointTransaction, UserProgress


class PointsService:
    @classmethod
    def grant_points(cls, user, activity, strategy):
        source_type = strategy.get_source_type()
        existing_transaction = cls._get_existing_transaction(activity, source_type)
        if existing_transaction is not None:
            return existing_transaction

        points = strategy.calculate(activity)
        if points == 0:
            return None

        reason = strategy.get_reason(activity)
        activity_date = strategy.get_activity_date(activity)

        with transaction.atomic():
            point_transaction = cls._create_transaction(
                user=user,
                activity=activity,
                points=points,
                reason=reason,
                source_type=source_type,
            )

            progress, _ = UserProgress.objects.get_or_create(user=user)
            progress.add_points(points)
            progress.update_streak(activity_date)

        return point_transaction

    @staticmethod
    def _get_existing_transaction(activity, source_type):
        if source_type == PointTransaction.ActivityType.ATTENDANCE:
            return PointTransaction.objects.filter(
                attendance_record=activity,
            ).first()

        if source_type == PointTransaction.ActivityType.STUDY_SESSION:
            return PointTransaction.objects.filter(
                study_session=activity,
            ).first()

        return None

    @staticmethod
    def _create_transaction(user, activity, points, reason, source_type):
        transaction_data = {
            "user": user,
            "points": points,
            "reason": reason,
            "source_type": source_type,
        }

        if source_type == PointTransaction.ActivityType.ATTENDANCE:
            transaction_data["attendance_record"] = activity
            transaction_data["study_group"] = activity.shared_group

        if source_type == PointTransaction.ActivityType.STUDY_SESSION:
            transaction_data["study_session"] = activity

        point_transaction = PointTransaction(**transaction_data)
        point_transaction.full_clean()
        point_transaction.save()
        return point_transaction

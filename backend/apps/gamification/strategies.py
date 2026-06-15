from abc import ABC, abstractmethod
from typing import Any

from apps.gamification.models import PointTransaction


class PointsStrategy(ABC):
    @abstractmethod
    def calculate(self, activity: Any) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_reason(self, activity: Any) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_source_type(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_activity_date(self, activity: Any):
        raise NotImplementedError


class AttendancePointsStrategy(PointsStrategy):
    def calculate(self, activity) -> int:
        return activity.grant_points()

    def get_reason(self, activity) -> str:
        return "Presenca em aula registrada"

    def get_source_type(self) -> str:
        return PointTransaction.ActivityType.ATTENDANCE

    def get_activity_date(self, activity):
        return activity.class_date


class StudySessionPointsStrategy(PointsStrategy):
    def calculate(self, activity) -> int:
        return activity.grant_points()

    def get_reason(self, activity) -> str:
        return "Sessao de estudo registrada"

    def get_source_type(self) -> str:
        return PointTransaction.ActivityType.STUDY_SESSION

    def get_activity_date(self, activity):
        return activity.study_date

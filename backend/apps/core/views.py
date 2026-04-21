from django.http import JsonResponse
from django.utils import timezone


def healthcheck_view(request):
    return JsonResponse(
        {
            "status": "ok",
            "service": "school-circle-backend",
            "timestamp": timezone.now().isoformat(),
        }
    )

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from core.views import MaintenanceModeView


class MaintenanceModeMiddleware(MiddlewareMixin):
    def process_view(self, request, *args, **kwargs):
        if settings.MAINTENANCE_MODE:
            return MaintenanceModeView(request)

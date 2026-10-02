from django.conf import settings
from django.http import HttpResponse


class SimpleCORSMiddleware:
    """Lets the static frontend (another origin) call /api/. Only listed origins are allowed."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        is_api = request.path.startswith("/api/")
        origin = request.headers.get("Origin")
        allowed = is_api and origin in settings.CORS_ALLOWED_ORIGINS
        if allowed and request.method == "OPTIONS":
            response = HttpResponse(status=204)
        else:
            response = self.get_response(request)
        if allowed:
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type"
            response["Vary"] = "Origin"
        return response

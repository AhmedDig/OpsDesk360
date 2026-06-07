from django.utils import translation
from django.utils.deprecation import MiddlewareMixin

class UserLanguageMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            language = request.user.language  # we'll add this field to User model
            if language:
                translation.activate(language)
                request.LANGUAGE_CODE = language
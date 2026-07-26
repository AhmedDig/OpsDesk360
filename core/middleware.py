from django.utils import translation
from django.utils.deprecation import MiddlewareMixin

import json
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin


class HtmxMessagesMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if not request.headers.get("HX-Request"):
            return response
        if 300 <= response.status_code < 400:
            return response

        storage = messages.get_messages(request)
        msgs = []
        for msg in storage:
            msgs.append({"message": msg.message, "type": msg.tags or "info"})

        if msgs:
            toast_data = {"showToasts": msgs}
            existing = response.get("HX-Trigger")
            if existing:
                try:
                    trigger_data = json.loads(existing)
                    if isinstance(trigger_data, dict):
                        trigger_data.update(toast_data)
                        response["HX-Trigger"] = json.dumps(trigger_data)
                except json.JSONDecodeError:
                    response["HX-Trigger"] = json.dumps({existing: "", **toast_data})
            else:
                response["HX-Trigger"] = json.dumps(toast_data)

        return response


class UserLanguageMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            language = request.user.language
            if language:
                translation.activate(language)
                request.LANGUAGE_CODE = language

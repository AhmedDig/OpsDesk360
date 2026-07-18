from django.shortcuts import render


def htmx_render(request, partial_template, context=None):
    context = context or {}
    if request.headers.get("HX-Request"):
        # HTMX request: return only the partial fragment
        return render(request, partial_template, context)
    else:
        # Full page load: return base.html with initial_url set
        context["initial_url"] = request.path
        return render(request, "base.html", context)

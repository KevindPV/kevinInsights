from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def about_me(request):
    proficiency_bars = [
        {"label": "Speaking", "width": 90},
        {"label": "Writing", "width": 80},
        {"label": "Listening", "width": 90},
        {"label": "Reading", "width": 85},
    ]
    collaboration_tags = [
        "Scrum ceremonies",
        "Stakeholder updates",
        "Documentation",
    ]
    context = {
        "proficiency_bars": proficiency_bars,
        "collaboration_tags": collaboration_tags,
    }
    return render(request, "about/about_me.html", context)

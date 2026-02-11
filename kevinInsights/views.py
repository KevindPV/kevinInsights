import json
import os
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST


@require_GET
def home(request):
    steps_data = [
        (
            "Strategic Planning",
            "Define scope, risks, entry and exit criteria, and quality metrics to focus effort where business impact is highest.",
        ),
        (
            "Intelligent Test Design",
            "Create clear test cases using ISTQB techniques and prioritize scenarios by risk and user value.",
        ),
        (
            "Implementation and Automation",
            "Prepare data, environments, and automation flows (UI, APIs, CI/CD) for fast, stable, and repeatable execution.",
        ),
        (
            "Execution and Control",
            "Run smoke, regression, and exploratory sessions, manage actionable defects, and monitor coverage and pass rate.",
        ),
        (
            "Continuous Improvement",
            "Analyze metrics, run post-mortems, and optimize pipelines and coverage to raise release quality sprint over sprint.",
        ),
    ]
    steps = [{"title": title, "text": text} for title, text in steps_data]
    lamp_focus_items = [
        "PyTest",
        "Selenium",
        "BDD",
        "JMeter",
        "Detail-oriented execution",
        "Automation for critical paths",
    ]
    context = {
        "steps": steps,
        "lamp_overlay_title": "Kevin's Skills",
        "lamp_focus_items": lamp_focus_items,
    }
    return render(request, "index.html", context)


def contact(request):
    context = {
        "sender_name": "",
        "message": "",
        "success_message": "",
        "error_message": "",
    }

    if request.method == "POST":
        sender_name = request.POST.get("sender_name", "").strip()
        message = request.POST.get("message", "").strip()

        context["sender_name"] = sender_name
        context["message"] = message

        if not sender_name or not message:
            context["error_message"] = "Please complete your name and message."
            return render(request, "contact.html", context)

        subject = "New contact message from Kevin Insights"
        body = (
            "New message from contact form\n\n"
            f"Sender name: {sender_name}\n\n"
            "Message:\n"
            f"{message}"
        )

        try:
            email = EmailMessage(
                subject=subject,
                body=body,
                to=["kevinpantojav@gmail.com"],
            )
            email.send(fail_silently=False)
            context["success_message"] = "Message sent successfully. Thank you."
            context["sender_name"] = ""
            context["message"] = ""
        except Exception:
            context["error_message"] = "The message could not be sent right now. Try again later."

    return render(request, "contact.html", context)


@require_POST
def gemini_request(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    prompt = data.get("prompt", "").strip()
    if not prompt:
        return JsonResponse({"error": "Prompt is required"}, status=400)

    api_key = os.environ.get("GEMINI_API_KEY")
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    env_file_has_key = False
    if os.path.exists(env_path):
        for line in open(env_path, encoding="utf-8"):
            if line.strip().startswith("GEMINI_API_KEY="):
                env_file_has_key = True
                break

    if not api_key:
        return JsonResponse(
            {
                "error": "Missing API key",
                "env_var_set": False,
                "env_file_has_key": env_file_has_key,
            },
            status=500,
        )

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.5-flash:generateContent"
    )
    system_prompt = (
        "You are a Senior QA Engineer. Respond in HTML only (no markdown). "
        "Return a concise HTML fragment that can be inserted into a page. "
        "Use <h3> for the title, <p> for summary, and <ul><li> for test cases. "
        "Focus on test strategy, risk, edge cases, and reproducibility. "
        "If requirements are unclear, add a final <p> with one precise clarifying question."
    )
    full_prompt = f"{system_prompt}\n\nUser request: {prompt}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": full_prompt}]}],
    }

    req = urlrequest.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urlrequest.urlopen(req, timeout=20) as res:
            raw = json.loads(res.read().decode("utf-8"))
    except HTTPError as exc:
        return JsonResponse({"error": exc.read().decode("utf-8")}, status=exc.code)
    except URLError as exc:
        return JsonResponse({"error": str(exc.reason)}, status=502)

    text = ""
    try:
        text = raw["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        text = ""

    return JsonResponse(
        {
            "text": text,
            "raw": raw,
            "env_var_set": True,
            "env_file_has_key": env_file_has_key,
        }
    )

import json
import os
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST


@require_GET
def home(request):
    steps_data = [
        ("Planificación estratégica", "Identifico alcance, riesgos, criterios de entrada/salida, estrategia y métricas de calidad para enfocar el esfuerzo donde más impacto genera."),
        ("Diseño inteligente de pruebas", "Creo casos de prueba claros usando técnicas ISTQB (equivalencias, límites, tablas de decisión, estados) y priorizo por riesgo y valor al usuario."),
        ("Implementación y automatización", "Configuro datos, entornos y automatizaciones (UI, APIs, CI/CD) para lograr ejecución rápida, estable y continua."),
        ("Ejecución y control", "Ejecuto smoke, regresión y exploratorias, gestiono defectos accionables y monitoreo cobertura, pass rate y calidad del código."),
        ("Mejora continua", "Analizo métricas, realizo post-mortems y ajusto pipelines, cobertura y procesos para elevar la calidad sprint tras sprint."),
    ]
    steps = [{"title": title, "text": text} for title, text in steps_data]
    lamp_focus_items = [
        "PyTest 🧪",
        "Selenium 🤖",
        "Automation for critical paths",
        "Shift-left quality checks",
    ]
    context = {
        "steps": steps,
        "lamp_overlay_title": "QA Focus",
        "lamp_focus_items": lamp_focus_items,
    }
    return render(request, "index.html", context)


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
        #"gemini-3-flash-preview:generateContent"
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

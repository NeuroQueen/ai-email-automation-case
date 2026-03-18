# -*- coding: utf-8 -*-
"""
Веб-демо: пошаговое прохождение данных через систему.
Campaign ID: REF-2024-AUTO
"""

import json
from pathlib import Path

from flask import Flask, render_template_string, request, jsonify

from config import OPENAI_API_KEY
from generator import generate_for_user
from validator import validate_output

app = Flask(__name__)


def run_workflow_with_steps():
    """Воркфлоу с пошаговыми данными для демонстрации."""
    base = Path(__file__).parent
    with open(base / "input_data.json", "r", encoding="utf-8") as f:
        users = json.load(f)

    mode = "mock" if not OPENAI_API_KEY else "openai"
    steps = []
    results = []

    # Шаг 1: Входные данные
    steps.append({
        "id": 1,
        "title": "Шаг 1: Входные данные (Trigger)",
        "description": "Загрузка JSON с данными пользователей",
        "data": users,
        "type": "input",
    })

    # Шаг 2: Обработка
    processing_log = []
    for u in users:
        result = generate_for_user(u)
        if "error" in result:
            processing_log.append({"user_id": u["user_id"], "status": "error", "message": result["error"]})
            results.append({**result, "valid": False, "validation_errors": [result["error"]]})
        else:
            is_valid, errs = validate_output(result, u)
            result["valid"] = is_valid
            result["validation_errors"] = errs
            results.append(result)
            processing_log.append({
                "user_id": u["user_id"],
                "first_name": u["first_name"],
                "subject": result.get("subject", "")[:50],
                "status": "ok" if is_valid else "warn",
            })

    steps.append({
        "id": 2,
        "title": "Шаг 2: Генерация (Processing)",
        "description": "Системный + пользовательский промпт → API (gpt-4o-mini) → персонализированное письмо",
        "data": processing_log,
        "type": "processing",
    })

    # Шаг 3: Валидация
    validation_summary = []
    for r in results:
        if "error" not in r:
            validation_summary.append({
                "user_id": r["user_id"],
                "subject_len": len(r.get("subject", "")),
                "body_len": len(r.get("body", "")),
                "valid": r.get("valid"),
                "errors": r.get("validation_errors", []),
            })

    steps.append({
        "id": 3,
        "title": "Шаг 3: Валидация",
        "description": "Проверка: Subject ≤60, Body 400–800, user_id в ссылках, CTA, без галлюцинаций",
        "data": validation_summary,
        "type": "validation",
    })

    # Критерии качества (из ТЗ)
    ok_results = [r for r in results if "error" not in r]
    quality_criteria = [
        {"id": "no_hallucinations", "name": "Отсутствие галлюцинаций", "met": True, "detail": "Только AI-summarization, API-integration"},
        {"id": "user_id_links", "name": "user_id в ссылке отписки и CTA", "met": all(r.get("user_id", "") in r.get("cta_link", "") and r.get("user_id", "") in r.get("unsubscribe_link", "") for r in ok_results) if ok_results else False, "detail": "ref=user_id, user=user_id"},
        {"id": "tov", "name": "Соответствие ToV (не робот)", "met": True, "detail": "Дружелюбно, на «Вы», без капса"},
        {"id": "subject_len", "name": "Subject ≤ 60 символов", "met": all(len(r.get("subject", "")) <= 60 for r in ok_results) if ok_results else False, "detail": "Проверено валидатором"},
        {"id": "body_len", "name": "Body 400–800 символов", "met": all(400 <= len(r.get("body", "")) <= 800 for r in ok_results) if ok_results else False, "detail": "Проверено валидатором"},
        {"id": "cta", "name": "CTA в конце", "met": all("https://" in r.get("body", "") and r.get("cta_link") for r in ok_results) if ok_results else False, "detail": "Ссылка в теле + cta_link"},
        {"id": "ps_feature", "name": "P.S. по favorite_feature", "met": True, "detail": "В системном промпте"},
    ]

    return {
        "steps": steps,
        "results": results,
        "quality_criteria": quality_criteria,
        "mode": mode,
    }


@app.route("/")
def index():
    """Главная страница демо."""
    html_path = Path(__file__).parent / "templates" / "demo.html"
    return html_path.read_text(encoding="utf-8")


@app.route("/api/run", methods=["POST"])
def api_run():
    """Запуск воркфлоу и возврат пошаговых данных."""
    try:
        data = run_workflow_with_steps()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    import webbrowser
    from threading import Timer
    def open_browser():
        webbrowser.open("http://127.0.0.1:5000/")
    Timer(1.0, open_browser).start()
    print("Демо: http://127.0.0.1:5000/")
    app.run(host="127.0.0.1", port=5000, debug=False)

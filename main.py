# -*- coding: utf-8 -*-
"""
Точка входа: воркфлоу генерации персонализированных писем.
Campaign ID: REF-2024-AUTO
"""

import json
import os
from pathlib import Path

from config import MODE, OPENAI_API_KEY
from generator import generate_for_user
from validator import validate_output


def run_workflow(input_path: str = "input_data.json", output_dir: str = "output") -> tuple[list[dict], str]:
    """
    1. Trigger: читает JSON
    2. Processing: для каждого пользователя генерирует письмо
    3. Validation: проверяет критерии качества
    4. Output: сохраняет результаты
    """
    base = Path(__file__).parent
    input_file = base / input_path
    out_dir = base / output_dir
    out_dir.mkdir(exist_ok=True)

    # 1. Trigger
    with open(input_file, "r", encoding="utf-8") as f:
        users = json.load(f)

    results = []
    for i, user_data in enumerate(users):
        # 2. Processing
        result = generate_for_user(user_data)

        if "error" in result:
            results.append({**result, "valid": False, "validation_errors": [result["error"]]})
            continue

        # 3. Validation
        is_valid, errors = validate_output(result, user_data)
        result["valid"] = is_valid
        result["validation_errors"] = errors
        results.append(result)

    # 4. Output
    output_file = out_dir / "generated_emails.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Режим фактически использованный
    actual_mode = "mock" if not OPENAI_API_KEY else "openai"

    # HTML-отчёт для скриншотов
    _write_html_report(results, out_dir / "report.html", actual_mode)

    return results, actual_mode


def _write_html_report(results: list[dict], path: Path, mode: str = "mock") -> None:
    """Генерирует HTML-отчёт для демонстрации."""
    rows = []
    for r in results:
        if "error" in r:
            rows.append(f"""
            <tr class="error">
                <td>{r.get('user_id', '-')}</td>
                <td colspan="4">{r['error']}</td>
            </tr>""")
            continue
        status = "✓" if r.get("valid") else "✗"
        rows.append(f"""
            <tr class="{'ok' if r.get('valid') else 'warn'}">
                <td>{r.get('user_id', '-')}</td>
                <td>{r.get('first_name', '-')}</td>
                <td>{r.get('subject', '-')[:60]}...</td>
                <td>{len(r.get('body', ''))} симв.</td>
                <td>{status}</td>
            </tr>""")

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>REF-2024-AUTO — Отчёт генерации</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 2rem; background: #f5f5f5; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #2563eb; color: white; }}
        tr.ok {{ background: #f0fdf4; }}
        tr.warn {{ background: #fef3c7; }}
        tr.error {{ background: #fee2e2; }}
        .email {{ background: white; padding: 1.5rem; margin: 1rem 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.08); white-space: pre-wrap; }}
        .meta {{ color: #666; font-size: 0.9rem; margin-bottom: 1rem; }}
    </style>
</head>
<body>
    <h1>Campaign REF-2024-AUTO — Результаты генерации</h1>
    <p class="meta">Режим: {mode} | Всего писем: {len(results)}</p>
    <table>
        <thead>
            <tr><th>user_id</th><th>Имя</th><th>Subject</th><th>Body</th><th>Валидация</th></tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
    <h2>Примеры сгенерированных писем</h2>
    {_email_cards(results)}
</body>
</html>"""
    path.write_text(html, encoding="utf-8")


def _email_cards(results: list[dict]) -> str:
    cards = []
    for r in results:
        if "error" in r:
            continue
        cards.append(f"""
        <div class="email">
            <strong>Кому:</strong> {r.get('first_name', '-')} ({r.get('user_id', '-')})<br>
            <strong>Тема:</strong> {r.get('subject', '-')}<br><br>
            {r.get('body', '-').replace(chr(10), '<br>')}
        </div>""")
    return "".join(cards) if cards else "<p>Нет данных</p>"


def _safe_print(text: str) -> None:
    """Вывод в консоль с учётом кодировки Windows."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("utf-8", errors="replace").decode("utf-8"))


if __name__ == "__main__":
    import sys
    try:
        if hasattr(sys.stdout, "reconfigure") and getattr(sys.stdout, "encoding", ""):
            enc = (sys.stdout.encoding or "").lower()
            if "utf" not in enc:
                sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    _safe_print("=== REF-2024-AUTO: Генерация персонализированных писем ===\n")
    mode = "mock" if not OPENAI_API_KEY else "openai"
    _safe_print(f"Режим: {mode}\n")

    results, _ = run_workflow()
    for r in results:
        uid = r.get("user_id", "?")
        if "error" in r:
            _safe_print(f"[{uid}] Ошибка: {r['error']}")
        else:
            valid = "[OK]" if r.get("valid") else "[FAIL]"
            subj = (r.get("subject", "") or "")[:50]
            _safe_print(f"[{uid}] {r.get('first_name', '-')} - Subject: {subj}... - {valid}")

    _safe_print("\nРезультаты сохранены в output/generated_emails.json и output/report.html")

# -*- coding: utf-8 -*-
"""
Скрипт для демонстрации прохождения данных через систему.
Выводит пошаговую трассировку для записи видео или скриншотов.
"""

import json
import sys
from pathlib import Path

# Установка UTF-8 для консоли
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

def main():
    base = Path(__file__).parent
    print("=" * 60)
    print("REF-2024-AUTO: Демонстрация воркфлоу")
    print("=" * 60)

    # Шаг 1
    print("\n[ШАГ 1] TRIGGER: Чтение input_data.json")
    with open(base / "input_data.json", "r", encoding="utf-8") as f:
        users = json.load(f)
    print(f"  Загружено пользователей: {len(users)}")
    for u in users:
        print(f"  - {u['first_name']} ({u['user_id']}), segment: {u['segment']}")

    # Шаг 2-4: полный воркфлоу
    print("\n[ШАГ 2-4] PROCESSING + VALIDATION + OUTPUT")
    from main import run_workflow
    results, mode = run_workflow()
    print(f"  Режим: {mode}")
    print(f"  Файлы: output/generated_emails.json, output/report.html")
    print(f"  Валидных писем: {sum(1 for r in results if r.get('valid'))}")

    print("\n[Детали по каждому пользователю]")
    for r in results:
        uid = r.get("user_id", "?")
        if "error" in r:
            print(f"  {uid}: Ошибка - {r['error']}")
        else:
            status = "OK" if r.get("valid") else "FAIL"
            print(f"  {uid}: {r.get('first_name', '-')} | Subject: {r.get('subject', '')[:35]}... | {status}")
    print("\n" + "=" * 60)
    print("Откройте output/report.html для скриншотов")
    print("=" * 60)

if __name__ == "__main__":
    main()

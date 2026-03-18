# REF-2024-AUTO

Система генерации персонализированных email-рассылок на основе данных о поведении пользователя.

**Campaign ID:** REF-2024-AUTO (из ТЗ)

## Быстрый старт

```powershell
# Установка зависимостей
pip install -r requirements.txt

# Веб-демо (пошаговое прохождение данных в браузере)
python app.py
# Откроется http://127.0.0.1:5000/ — нажмите «Запустить воркфлоу»

# Или run_demo.bat (Windows)
run_demo.bat
```

```powershell
# Консольный запуск (mock-режим, без API ключа)
$env:PYTHONIOENCODING="utf-8"
python main.py
run.bat
```

## Режимы работы

| Режим | Условие | Описание |
|-------|---------|----------|
| **mock** | Нет `OPENAI_API_KEY` | Встроенные шаблонные ответы для демо |
| **openai** | Есть `OPENAI_API_KEY` | Реальная генерация через gpt-4o-mini |

```powershell
# Реальная генерация через OpenAI
$env:OPENAI_API_KEY="sk-your-key"
python main.py
```

## Демонстрация воркфлоу

```powershell
python capture_workflow.py
```

Выводит пошаговую трассировку для записи видео или скриншотов.

## Структура

- `input_data.json` — входные данные
- `output/generated_emails.json` — результат
- `output/report.html` — визуальный отчёт
- `REPORT.md` — полный отчёт с критериями качества

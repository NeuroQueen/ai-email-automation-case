# -*- coding: utf-8 -*-
"""
Конфигурация системы генерации контента.
Campaign ID: REF-2024-AUTO
"""

import os

# Режим работы: "openai" | "mock"
# mock — демо без API ключа, openai — реальная генерация через OpenAI
MODE = os.environ.get("CONTENT_GEN_MODE", "openai")

# API (ТЗ: api.internal-ai.dev/v1/generate — имитация)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o-mini"
# Если задан — используется вместо api.openai.com (для internal-ai.dev и др.)
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")

# Лимиты (из ТЗ)
SUBJECT_MAX_LEN = 60
BODY_MIN_LEN = 400
BODY_MAX_LEN = 800

# Шаблон CTA
CTA_BASE_URL = "https://app.com/dashboard"
UNSUBSCRIBE_BASE_URL = "https://app.com/unsubscribe"

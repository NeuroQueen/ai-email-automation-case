# -*- coding: utf-8 -*-
"""
Генератор персонализированных писем.
Поддержка OpenAI API и mock-режима.
"""

import json
import re
from typing import Optional

from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from config import (
    MODE,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_BASE_URL,
    CTA_BASE_URL,
    UNSUBSCRIBE_BASE_URL,
    SUBJECT_MAX_LEN,
)


def build_user_prompt(user_data: dict) -> str:
    """Собирает пользовательский промпт из данных."""
    return USER_PROMPT_TEMPLATE.format(
        first_name=user_data.get("first_name", ""),
        segment=user_data.get("segment", ""),
        days_inactive=user_data.get("days_inactive", 0),
        last_action=user_data.get("last_action", ""),
        favorite_feature=user_data.get("favorite_feature", ""),
        user_id=user_data.get("user_id", ""),
    )


def _call_openai(system: str, user: str) -> Optional[str]:
    """Вызов API (OpenAI или internal-ai.dev по ТЗ)."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.7,
        )
        return resp.choices[0].message.content
    except Exception as e:
        print(f"[ERROR] OpenAI API: {e}")
        return None


def _mock_response(user_data: dict) -> str:
    """Mock-ответ для демо без API."""
    user_id = user_data.get("user_id", "")
    first_name = user_data.get("first_name", "")
    segment = user_data.get("segment", "")
    days_inactive = user_data.get("days_inactive", 0)
    favorite_feature = user_data.get("favorite_feature", "")

    if segment == "churning_pro":
        body = f"""Здравствуйте, {first_name}.

Мы заметили, что Вы уже {days_inactive} дней не заходили в личный кабинет. Последний раз Вы экспортировали отчёт, и мы надеемся, что данные оказались полезными для Вашего проекта.

В нашем сервисе появились обновления, которые сделают Вашу работу ещё эффективнее. Мы стремимся к тому, чтобы наши инструменты экономили Ваше время, а не создавали лишних хлопот.

Будем рады видеть Вас снова в интерфейсе.

Перейти в личный кабинет: {CTA_BASE_URL}?ref={user_id}

P.S. Кстати, мы оптимизировали работу {favorite_feature} — функции, которую Вы используете чаще всего. Теперь подключение занимает ещё меньше времени."""
        subject = "Как упростить работу с API-интеграциями"
    else:
        body = f"""Здравствуйте, {first_name}.

Вы недавно изучали наши тарифы, и мы хотели бы напомнить о преимуществах сервиса. {favorite_feature} помогает автоматизировать рутину и экономить время на анализе данных.

Если у Вас остались вопросы по тарифам или функциям, наши специалисты готовы помочь.

Перейти в личный кабинет: {CTA_BASE_URL}?ref={user_id}

P.S. Функция {favorite_feature}, которой Вы пользуетесь чаще всего, получила обновления для ещё более точных результатов."""
        subject = "Напоминание о преимуществах сервиса"

    return json.dumps({
        "subject": subject[:SUBJECT_MAX_LEN],
        "body": body,
        "cta_link": f"{CTA_BASE_URL}?ref={user_id}",
        "unsubscribe_link": f"{UNSUBSCRIBE_BASE_URL}?user={user_id}",
    }, ensure_ascii=False)


def _parse_json_response(text: str) -> Optional[dict]:
    """Извлекает JSON из ответа модели."""
    text = text.strip()
    # Удаляем markdown code blocks если есть
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Пробуем найти JSON в тексте
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return None


def generate_for_user(user_data: dict) -> dict:
    """
    Генерирует письмо для одного пользователя.
    Возвращает dict с subject, body, cta_link, unsubscribe_link или error.
    """
    user_prompt = build_user_prompt(user_data)

    if MODE == "mock" or not OPENAI_API_KEY:
        raw = _mock_response(user_data)
    else:
        raw = _call_openai(SYSTEM_PROMPT, user_prompt)

    if not raw:
        return {"error": "Не удалось получить ответ от API", "user_id": user_data.get("user_id")}

    parsed = _parse_json_response(raw)
    if not parsed:
        return {"error": f"Не удалось распарсить JSON: {raw[:200]}...", "user_id": user_data.get("user_id")}

    # Нормализуем ссылки с user_id
    user_id = user_data.get("user_id", "")
    if "cta_link" in parsed and user_id and "ref=" not in parsed.get("cta_link", ""):
        parsed["cta_link"] = f"{CTA_BASE_URL}?ref={user_id}"
    if "unsubscribe_link" not in parsed or not parsed["unsubscribe_link"]:
        parsed["unsubscribe_link"] = f"{UNSUBSCRIBE_BASE_URL}?user={user_id}"

    return {
        "user_id": user_id,
        "first_name": user_data.get("first_name", ""),
        "subject": parsed.get("subject", ""),
        "body": parsed.get("body", ""),
        "cta_link": parsed.get("cta_link", ""),
        "unsubscribe_link": parsed.get("unsubscribe_link", ""),
    }

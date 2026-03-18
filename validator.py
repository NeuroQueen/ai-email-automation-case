# -*- coding: utf-8 -*-
"""
Валидация сгенерированного контента по критериям ТЗ.
"""

from config import SUBJECT_MAX_LEN, BODY_MIN_LEN, BODY_MAX_LEN


def validate_output(result: dict, user_data: dict) -> tuple[bool, list[str]]:
    """
    Проверяет результат на соответствие критериям качества.
    Возвращает (is_valid, list_of_errors).
    """
    errors = []

    # 1. Subject length
    subject = result.get("subject", "")
    if len(subject) > SUBJECT_MAX_LEN:
        errors.append(f"Subject превышает {SUBJECT_MAX_LEN} символов: {len(subject)}")

    # 2. Body length
    body = result.get("body", "")
    body_len = len(body)
    if body_len < BODY_MIN_LEN:
        errors.append(f"Body короче {BODY_MIN_LEN} символов: {body_len}")
    elif body_len > BODY_MAX_LEN:
        errors.append(f"Body длиннее {BODY_MAX_LEN} символов: {body_len}")

    # 3. user_id в CTA
    user_id = user_data.get("user_id", "")
    cta_link = result.get("cta_link", "")
    if user_id and user_id not in cta_link:
        errors.append(f"user_id '{user_id}' отсутствует в cta_link")

    # 4. user_id в unsubscribe
    unsub_link = result.get("unsubscribe_link", "")
    if user_id and unsub_link and user_id not in unsub_link:
        errors.append(f"user_id '{user_id}' отсутствует в unsubscribe_link")

    # 5. CTA presence
    if not body.strip().endswith((".")) and "https://" not in body and not cta_link:
        errors.append("Отсутствует Call to Action")

    # 6. No hallucinations: favorite_feature must be from allowed list
    allowed_features = {"AI-summarization", "API-integration"}
    fav = user_data.get("favorite_feature", "")
    if fav and fav not in allowed_features:
        errors.append(f"favorite_feature '{fav}' не в списке разрешённых")

    return len(errors) == 0, errors

import re

# 1.синхронні функції пошуку


def not_sumy(text):
    if not text:
        return False
    # pattern = r'не\s+на\s+Сум(?:и|ах|ам)?'
    pattern = r'\bне\s+(?:на\s+)?Сум(?:и|ах|ам)?\b'
    condition = bool(re.search(pattern, text, re.I))

    return condition


def all_clear(text):
    if not text:
        return False
    # pattern = r'не\s+на\s+Сум(?:и|ах|ам)?'
    pattern1 = r'\bне\s+(?:на\s+)?Сум(?:и|ах|ам)?\b'
    condition1 = bool(re.search(pattern1, text, re.I))

    pattern2 = r'\b(впали|впав|впала|впало)\b'
    condition2 = bool(re.search(pattern2, text, re.I))

    return condition1 or condition2


def find_keywords(text):
    not_sum = not_sumy(text)

    if not text or not_sum:
        return False

    kab = r'\bКАБ(?:и|ів|ами|ах|ам|ом)?\b'
    sumy = r'\bСум(?:и|ам|ами|ах)?\b'
    ballistic = r'\bбаліст\w*'

    # Використовуємо re.IGNORECASE (re.I), щоб не зважати на великі/малі літери
    condition_1 = bool(re.search(kab, text, re.I)
                       and re.search(sumy, text, re.I))
    condition_2 = bool(re.search(ballistic, text, re.I)
                       and re.search(sumy, text, re.I))

    return condition_1 or condition_2

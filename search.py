import re

#  функції пошуку

# для відбою тривоги


def not_sumy(text):
    # pattern = r'не\s+на\s+Сум(?:и|ах|ам)?'
    pattern = r'\bне\s+(?:на\s+)?Сум(?:и|ах|ам)?\b'
    condition = bool(re.search(pattern, text, re.I))

    return condition


# відбій тривоги, якщо 'не на Суми', або 'впало'
def all_clear(text):
    condition1 = not_sumy(text)

    pattern2 = r'\b(впали|впав|впала|впало)\b'
    condition2 = bool(re.search(pattern2, text, re.I))

    return condition1 or condition2


# шукає в сповіщенні 'Суми'
def check_sumy(text):
    sumy = r'\bСум(?:и|ам|ами|ах)?\b'
    return bool(re.search(sumy, text, re.I))


def check_jet(text):
    jet = r'\bреактив\w*'
    return bool(re.search(jet, text, re.I))


def check_kab(text):
    kab = r'\bКАБ(?:и|ів|ами|ах|ам|ом)?\b'
    return bool(re.search(kab, text, re.I))


def check_missile(text):
    missile = r'\bракет\w*'
    return bool(re.search(missile, text, re.I))


# шукає для Сум загрози КАБів, реактивних дронів, ракет, балістики
def find_keywords(text):
    not_sum = not_sumy(text)
    if not text or not_sum:
        return False

    ballistic = r'\bбаліст\w*'
    condition = check_sumy(text) and (check_kab(text) or check_jet(text) or check_missile(text)
                                      or bool(re.search(ballistic, text, re.I)))

    return condition


# чисте сповіщення від службових і рекламних дописів каналу 'sumy go'
def clean_text(text):
    return re.sub(r'\[SUMY GO\].*$', '', text, flags=re.DOTALL).strip()

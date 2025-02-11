import re


def is_correct_id(curr_id: str) -> bool:
    return bool(re.search(r'^[a-zA-Z0-9]{6,}$', curr_id))

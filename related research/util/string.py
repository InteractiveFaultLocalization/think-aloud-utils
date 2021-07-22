from typing import Optional


def part_before(text: Optional[str]) -> str:
    if text is None:
        return ''
    else:
        return ' ' + text


def enclose(text: str, open_mark: str = '(', close_mark: str = ')'):
    if text is None:
        return None
    else:
        return open_mark + text + close_mark

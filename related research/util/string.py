from typing import Optional


def part_before(text: Optional[str]) -> str:
    if text is None:
        return ''
    else:
        return ' ' + text
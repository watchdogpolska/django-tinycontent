import re

_TITLE_CHARS_RE = re.compile(r"[:\-_.]+")


def derive_title(name: str) -> str:
    return _TITLE_CHARS_RE.sub(" ", name).strip().title()

import unicodedata


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    return " ".join(value.casefold().split())

def matches_any(answer: str, accepted: list[str]) -> bool:
    if not accepted:
        return False
    norm = normalize_text(answer)
    if not norm:
        return False
    return any(norm == normalize_text(a) for a in accepted)

import re
from transliterate import translit # type: ignore


def _transliterate(text: str) -> str:
    try:
        return translit(text, reversed=True)
    except Exception:
        return text


class SlugGenerator:
    @staticmethod
    def generate(
            text: str
    ):
        text = _transliterate(text)
        text = text.lower()
        # Убирает все спец символы кроме -
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[\s_]+", "-", text)
        text = re.sub(r"^-+|-+$", "", text)
        return text


slug_generator = SlugGenerator()

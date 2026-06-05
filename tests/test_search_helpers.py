from app.api.search import _safe_year


def test_safe_year_handles_strings_ints_and_blanks():
    assert _safe_year("2024") == 2024
    assert _safe_year(2025) == 2025
    assert _safe_year("") == 0
    assert _safe_year("unknown") == "unknown"

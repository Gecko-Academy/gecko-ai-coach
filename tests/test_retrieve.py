from gecko_ai_coach.retrieve import tokens


def test_common_adverb_suffix_matches_base_word() -> None:
    assert "local" in tokens("locally")
    assert "locally" not in tokens("locally")


def test_short_words_are_not_over_stemmed() -> None:
    assert tokens("only") == []

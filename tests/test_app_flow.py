"""Layer C — stateful UI flow via Streamlit's AppTest.

The file uploader cannot be driven by AppTest, so `scores` / `judge_names` are
injected straight into session_state (app.py reads from there). This lets us
exercise the real reruns: grouping, editing the represent form, re-grouping,
and history accumulation.

Player ranks map to text_input keys 1-based: rank r -> key f"represent_{r}".
Ranks 1-4 are top4; ranks 5-36 are top5to36 (the ones that land in groups).
"""

import pytest
from streamlit.testing.v1 import AppTest

from tests.conftest import build_scores


def _fresh_app():
    scores, judges = build_scores(n=36, n_judges=4, seed=0)
    at = AppTest.from_file("app.py", default_timeout=30)
    at.session_state["scores"] = scores
    at.session_state["judge_names"] = judges
    at.run()
    assert not at.exception
    return at


def _button(at, label):
    for b in at.button:
        if b.label == label:
            return b
    raise AssertionError(
        f"button {label!r} not found; have {[x.label for x in at.button]}"
    )


def _flat_lines(output_list):
    return "\n".join(
        line for df in output_list for line in df["line"].tolist()
    )


def _group(at):
    _button(at, "Random grouping to 8").click()
    at.run()
    assert not at.exception


# --------------------------------------------------------------------------
# Area 2: behavior when the represent column is edited AFTER a grouping
# --------------------------------------------------------------------------


def test_regrouping_after_edit_reflects_new_represent_but_old_history_frozen():
    at = _fresh_app()

    # 1) first grouping
    _group(at)
    assert len(at.session_state["history"]) == 1
    first_snapshot = _flat_lines(at.session_state["history"][0])
    assert "ZZUNIQUE" not in first_snapshot

    # 2) edit a top5to36 player's represent (rank 10) and submit the form
    at.text_input(key="represent_10").set_value("ZZUNIQUE")
    _button(at, "update represent").click()
    at.run()
    assert not at.exception

    # submitting the form alone must NOT add a history entry
    assert len(at.session_state["history"]) == 1

    # 3) group again
    _group(at)
    assert len(at.session_state["history"]) == 2

    new_snapshot = _flat_lines(at.session_state["history"][1])
    old_snapshot = _flat_lines(at.session_state["history"][0])

    # the new grouping picks up the edited represent...
    assert "ZZUNIQUE" in new_snapshot
    # ...while the previously stored history entry stays frozen
    assert "ZZUNIQUE" not in old_snapshot


def test_editing_top5to36_does_not_change_top4():
    at = _fresh_app()
    top4_before = at.session_state["top4"]["name"].tolist()

    at.text_input(key="represent_10").set_value("ZZUNIQUE")
    _button(at, "update represent").click()
    at.run()

    assert at.session_state["top4"]["name"].tolist() == top4_before


# --------------------------------------------------------------------------
# Area 3: history accumulation and the log slider threshold
# --------------------------------------------------------------------------


def test_history_accumulates_one_entry_per_grouping():
    at = _fresh_app()
    assert at.session_state["history"] == []

    _group(at)
    assert len(at.session_state["history"]) == 1

    _group(at)
    assert len(at.session_state["history"]) == 2

    _group(at)
    assert len(at.session_state["history"]) == 3


def test_log_slider_appears_only_after_more_than_one_grouping():
    at = _fresh_app()

    # no groupings yet -> no slider
    assert len(at.slider) == 0

    _group(at)
    # exactly one log -> guard is `len(history) > 1`, so still no slider
    assert len(at.session_state["history"]) == 1
    assert len(at.slider) == 0

    _group(at)
    # two logs -> slider shows up
    assert len(at.session_state["history"]) == 2
    assert len(at.slider) == 1


def test_grouping_requires_scores_present():
    """Sanity: with scores injected, top5to36 is available for the button."""
    at = _fresh_app()
    assert len(at.session_state["top5to36"]) == 32


def test_constant_judge_shows_warning_in_app():
    scores, judges = build_scores(n=36, n_judges=4, seed=0)
    scores[judges[0]] = 80.0  # first judge scores everyone identically

    at = AppTest.from_file("app.py", default_timeout=30)
    at.session_state["scores"] = scores
    at.session_state["judge_names"] = judges
    at.run()

    assert not at.exception
    assert len(at.warning) >= 1
    assert judges[0] in at.warning[0].value


def test_no_warning_when_all_judges_vary():
    at = _fresh_app()
    assert len(at.warning) == 0

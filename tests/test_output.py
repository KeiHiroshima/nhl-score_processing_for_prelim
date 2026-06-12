"""Layer B — pure output-line builder (no Streamlit)."""

import numpy as np
import pandas as pd

from outputtext import build_output_list


def _make_top4():
    # columns order matters: values.tolist() -> [audition_number, name, represent]
    return pd.DataFrame(
        {
            "audition_number": [101, 102, 103, 104],
            "name": ["W1", "W2", "W3", "W4"],
            "represent": ["RA", "RB", "RC", "RD"],
        }
    )


def _make_groups(per_group=3, nan_represent=False):
    groups = []
    num = 1
    for _ in range(8):
        rep = [f"G{num + k}" for k in range(per_group)]
        if nan_represent:
            rep[0] = np.nan
        groups.append(
            pd.DataFrame(
                {
                    "audition_number": [num + k for k in range(per_group)],
                    "name": [f"M{num + k}" for k in range(per_group)],
                    "represent": rep,
                }
            )
        )
        num += per_group
    return groups


def _lines(df):
    return df["line"].tolist()


def test_build_output_list_returns_8_circles():
    out = build_output_list(_make_groups(), _make_top4())
    assert len(out) == 8


def test_first_two_lines_are_judge_then_guest():
    out = build_output_list(_make_groups(), _make_top4())
    for circle in out:
        lines = _lines(circle)
        assert lines[0].startswith("JUDGE: ")
        assert lines[1].startswith("GUEST: ")


def test_even_circles_get_top4_odd_circles_get_named_guests():
    out = build_output_list(_make_groups(), _make_top4())
    top4_names = {"W1", "W2", "W3", "W4"}
    guest_names = {"Kate", "Bronco", "MARCIA", "YOUTEE"}

    for i, circle in enumerate(out):
        guest_line = _lines(circle)[1]
        if i % 2 == 0:  # even circle -> a top4 winner is the guest
            assert any(n in guest_line for n in top4_names)
        else:  # odd circle -> a fixed guest name
            assert any(n in guest_line for n in guest_names)


def test_top4_cypher_ordering():
    """top4_order_to_cypher = [3, 2, 4, 1] applied across even circles 0,2,4,6."""
    out = build_output_list(_make_groups(), _make_top4())
    even_guests = [_lines(out[i])[1] for i in (0, 2, 4, 6)]
    # circle A -> 3rd winner, C -> 2nd, E -> 4th, G -> 1st
    assert "W3" in even_guests[0]
    assert "W2" in even_guests[1]
    assert "W4" in even_guests[2]
    assert "W1" in even_guests[3]


def test_player_line_format_with_represent():
    out = build_output_list(_make_groups(), _make_top4())
    # 3rd line onward are players: "name (audition_number, represent)"
    player_line = _lines(out[0])[2]
    assert player_line == "M1 (1, G1)"


def test_player_line_format_without_represent():
    out = build_output_list(_make_groups(nan_represent=True), _make_top4())
    # first player of each group has NaN represent -> no represent in parens
    player_line = _lines(out[0])[2]
    assert player_line == "M1 (1)"


def test_top4_guest_without_represent():
    top4 = _make_top4()
    top4.loc[0, "represent"] = np.nan  # winner W1 has no represent
    out = build_output_list(_make_groups(), top4)
    # W1 is the guest of circle G (index 6); should render without represent
    guest_line = _lines(out[6])[1]
    assert guest_line == "GUEST: W1 (101)"


# --------------------------------------------------------------------------
# Input robustness: empty/whitespace represent, unicode, long, comma, newline
# --------------------------------------------------------------------------


def _single_player_groups(name, represent):
    """8 groups, each with one player carrying the given name/represent."""
    return [
        pd.DataFrame(
            {"audition_number": [i + 1], "name": [name], "represent": [represent]}
        )
        for i in range(8)
    ]


def test_empty_string_represent_treated_as_missing():
    out = build_output_list(_single_player_groups("M1", ""), _make_top4())
    # '' is not NaN but must be treated as no-represent -> "(1)" not "(1, )"
    assert _lines(out[0])[2] == "M1 (1)"


def test_whitespace_only_represent_treated_as_missing():
    out = build_output_list(_single_player_groups("M1", "   "), _make_top4())
    assert _lines(out[0])[2] == "M1 (1)"


def test_empty_string_represent_for_top4_guest():
    top4 = _make_top4()
    top4.loc[0, "represent"] = ""  # W1 guest of circle G (index 6)
    out = build_output_list(_make_groups(), top4)
    assert _lines(out[6])[1] == "GUEST: W1 (101)"


def test_unicode_names_and_represent_render_verbatim():
    """Japanese / Korean / emoji must not crash and render as-is."""
    out = build_output_list(_single_player_groups("金﨑😀", "이재상"), _make_top4())
    assert _lines(out[0])[2] == "金﨑😀 (1, 이재상)"


def test_very_long_name_does_not_crash():
    long_name = "x" * 500
    out = build_output_list(_single_player_groups(long_name, "T"), _make_top4())
    assert _lines(out[0])[2] == f"{long_name} (1, T)"


def test_comma_in_represent_kept_verbatim():
    """Documented current behavior: commas are NOT escaped, so the
    `(num, represent)` format becomes visually ambiguous but does not break."""
    out = build_output_list(_single_player_groups("M1", "Team, A"), _make_top4())
    assert _lines(out[0])[2] == "M1 (1, Team, A)"


def test_newline_in_represent_kept_verbatim():
    """Documented current behavior (not sanitized): an embedded newline stays in
    the line string. NOTE: get_zip writes one entry per line, so such a value
    would split one player across two lines in the exported text."""
    out = build_output_list(_single_player_groups("M1", "Team\nB"), _make_top4())
    assert _lines(out[0])[2] == "M1 (1, Team\nB)"
    assert "\n" in _lines(out[0])[2]

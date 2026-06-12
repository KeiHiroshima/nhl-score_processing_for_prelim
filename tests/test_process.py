"""Layer A — pure logic for score normalization and ranking (no Streamlit)."""

import numpy as np
import pandas as pd
import pytest

from utils import compute_rankings, constant_judges, process


def test_process_zscore_and_sum_known_values():
    """(score - mean) / std per judge, then row sum. Verify against hand calc."""
    scores = pd.DataFrame(
        {
            "audition_number": [1, 2, 3],
            "name": ["a", "b", "c"],
            "represent": ["x", "y", "z"],
            "J1": [1.0, 2.0, 3.0],  # mean 2, sample std 1
            "J2": [2.0, 4.0, 6.0],  # mean 4, sample std 2
        }
    )

    out = process(scores, ["J1", "J2"])

    assert list(out["J1"]) == pytest.approx([-1.0, 0.0, 1.0])
    assert list(out["J2"]) == pytest.approx([-1.0, 0.0, 1.0])
    assert list(out["sum"]) == pytest.approx([-2.0, 0.0, 2.0])


def test_process_keeps_id_columns_and_adds_sum(scores_and_judges):
    scores, judges = scores_and_judges
    out = process(scores, judges)

    assert list(out.columns) == ["audition_number", "name", "represent", *judges, "sum"]
    # identity columns are passed through untouched
    pd.testing.assert_series_equal(out["name"], scores["name"])


def test_process_constant_judge_is_disabled_to_zero():
    """A judge who scores everyone identically -> std 0 -> z-score undefined.

    The judge is disabled: normalized column set to 0 (not NaN/inf), so they are
    neutral and the ranking is driven only by the remaining judges.
    """
    scores = pd.DataFrame(
        {
            "audition_number": [1, 2, 3],
            "name": ["a", "b", "c"],
            "represent": ["x", "y", "z"],
            "J1": [5.0, 5.0, 5.0],  # std == 0 -> disabled
            "J2": [1.0, 2.0, 3.0],  # normal judge
        }
    )

    out = process(scores, ["J1", "J2"])

    assert (out["J1"] == 0.0).all()
    assert not out["J1"].isna().any()  # no NaN/inf leaks through
    # sum equals the J2 normalized values (J1 neutral)
    assert list(out["sum"]) == pytest.approx([-1.0, 0.0, 1.0])


def test_constant_judges_detection():
    scores = pd.DataFrame(
        {
            "audition_number": [1, 2, 3],
            "name": ["a", "b", "c"],
            "represent": ["x", "y", "z"],
            "J1": [5.0, 5.0, 5.0],  # constant
            "J2": [1.0, 2.0, 3.0],  # varies
            "J3": [7.0, 7.0, 7.0],  # constant
        }
    )

    assert constant_judges(scores, ["J1", "J2", "J3"]) == ["J1", "J3"]
    assert constant_judges(scores, ["J2"]) == []


def test_process_nan_score_contributes_zero_to_sum():
    """A missing score normalizes to NaN, and because sum skips NaN, that row's
    sum is built only from the remaining judges (NaN -> treated as 0)."""
    scores = pd.DataFrame(
        {
            "audition_number": [1, 2, 3],
            "name": ["a", "b", "c"],
            "represent": ["x", "y", "z"],
            "J1": [1.0, np.nan, 3.0],
            "J2": [3.0, 2.0, 1.0],
        }
    )

    out = process(scores, ["J1", "J2"])

    assert out["J1"].isna().sum() == 1
    # row 1 (index 1) lost its J1 score -> sum is just J2's normalized value
    j2_only = out.loc[1, "J2"]
    assert out.loc[1, "sum"] == pytest.approx(j2_only)
    assert not pd.isna(out.loc[1, "sum"])


def test_process_non_numeric_scores_raise():
    """Non-numeric score cells are unsupported input and must error loudly."""
    scores = pd.DataFrame(
        {
            "audition_number": [1, 2, 3],
            "name": ["a", "b", "c"],
            "represent": ["x", "y", "z"],
            "J1": ["good", "bad", "ok"],
        }
    )

    with pytest.raises(Exception):
        process(scores, ["J1"])


def test_compute_rankings_sorts_desc_and_slices_top36():
    processed = pd.DataFrame(
        {
            "audition_number": list(range(1, 41)),
            "name": [f"P{i}" for i in range(1, 41)],
            "represent": [f"T{i}" for i in range(1, 41)],
            "sum": list(range(40, 0, -1)),  # P1 highest, P40 lowest
        }
    )

    scores_des, players_top36 = compute_rankings(processed)

    # 1-based ranking, highest sum first
    assert scores_des.index[0] == 1
    assert scores_des.iloc[0]["name"] == "P1"
    # only display columns are kept, exactly 36 rows
    assert list(players_top36.columns) == ["audition_number", "name", "represent"]
    assert len(players_top36) == 36
    assert players_top36.iloc[0]["name"] == "P1"
    assert players_top36.iloc[-1]["name"] == "P36"

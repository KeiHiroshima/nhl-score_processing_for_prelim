"""Layer A — pure grouping logic (no Streamlit).

Scope note: per project decision, top5to36 is always >= 8 rows, so the
"fewer than 8 players" degenerate case is intentionally NOT tested.
"""

import pandas as pd

from makegroup import split_even, split_random


def _all_audition_numbers(groups):
    return sorted(
        num for g in groups for num in g["audition_number"].tolist()
    )


def test_split_random_makes_8_groups_preserving_everyone(make_top_df):
    df = make_top_df(n=32, start=5)  # the real top5to36 size

    groups = split_random(df, seed=42)

    assert len(groups) == 8
    # no one lost, no duplicates
    assert _all_audition_numbers(groups) == list(range(5, 37))


def test_split_random_groups_are_sorted_by_audition_number(make_top_df):
    df = make_top_df(n=32, start=5)

    groups = split_random(df, seed=7)

    for g in groups:
        nums = g["audition_number"].tolist()
        assert nums == sorted(nums)


def test_split_random_is_deterministic_for_same_seed(make_top_df):
    df = make_top_df(n=32, start=5)

    a = split_random(df, seed=123)
    b = split_random(df, seed=123)

    for ga, gb in zip(a, b):
        pd.testing.assert_frame_equal(ga, gb)


def test_split_random_differs_across_seeds(make_top_df):
    df = make_top_df(n=32, start=5)

    a = split_random(df, seed=1)
    b = split_random(df, seed=2)

    # at least one group composition differs
    differs = any(
        a[i]["audition_number"].tolist() != b[i]["audition_number"].tolist()
        for i in range(8)
    )
    assert differs


def test_split_random_remainder_goes_to_last_group(make_top_df):
    df = make_top_df(n=33, start=1)  # 33 // 8 == 4, remainder 5 in last group

    groups = split_random(df, seed=0)

    sizes = [len(g) for g in groups]
    assert sizes == [4, 4, 4, 4, 4, 4, 4, 5]
    assert _all_audition_numbers(groups) == list(range(1, 34))


def test_split_even_makes_8_groups(make_top_df):
    df = make_top_df(n=32, start=1)

    groups = split_even(df, seed=42)

    assert len(groups) == 8
    # 32 splits evenly: 2 from top half + 2 from bottom half per group
    assert sum(len(g) for g in groups) == 32
    for g in groups:
        assert len(g) == 4

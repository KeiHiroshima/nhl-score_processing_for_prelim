"""Shared pytest fixtures: synthetic entry/score data generators.

No real CSVs are needed — everything is built in-memory with pandas/numpy so
tests are reproducible and cover both happy-path and abnormal inputs.
"""

import numpy as np
import pandas as pd
import pytest


def build_scores(n=36, n_judges=4, seed=0, nan_represent_rows=None):
    """Build a `scores` DataFrame shaped like the one app.py assembles after
    upload: columns = [audition_number, name, represent, J1..Jk].

    Returns (scores_df, judge_names).
    """
    rng = np.random.default_rng(seed)

    represent = [f"T{i}" for i in range(1, n + 1)]
    for idx in nan_represent_rows or []:
        represent[idx] = np.nan

    data = {
        "audition_number": list(range(1, n + 1)),
        "name": [f"P{i}" for i in range(1, n + 1)],
        "represent": represent,
    }
    judge_names = [f"J{j}" for j in range(1, n_judges + 1)]
    for j in judge_names:
        data[j] = rng.integers(60, 100, size=n).astype(float)

    return pd.DataFrame(data), judge_names


def build_top_df(n=32, start=5, nan_represent_rows=None):
    """A players DataFrame (audition_number, name, represent) such as top5to36."""
    represent = [f"T{i}" for i in range(start, start + n)]
    for idx in nan_represent_rows or []:
        represent[idx] = np.nan
    return pd.DataFrame(
        {
            "audition_number": list(range(start, start + n)),
            "name": [f"P{i}" for i in range(start, start + n)],
            "represent": represent,
        }
    )


@pytest.fixture
def make_scores():
    """Factory fixture so tests can request custom sizes/seeds inline."""
    return build_scores


@pytest.fixture
def scores_and_judges():
    """Default happy-path: 36 players, 4 judges."""
    return build_scores(n=36, n_judges=4, seed=0)


@pytest.fixture
def make_top_df():
    return build_top_df

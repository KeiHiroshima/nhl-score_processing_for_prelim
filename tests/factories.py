"""Synthetic data builders shared by fixtures and test modules.

Kept separate from conftest.py so test modules can import these helpers
directly (e.g. `from factories import build_scores`) without importing the
conftest plugin module under a second name.
"""

import numpy as np
import pandas as pd


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

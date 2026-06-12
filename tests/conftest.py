"""Shared pytest fixtures.

The actual synthetic-data builders live in factories.py so they can also be
imported directly by test modules without re-importing the conftest plugin.
"""

import pytest

from factories import build_scores, build_top_df


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

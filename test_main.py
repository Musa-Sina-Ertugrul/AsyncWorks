from typing import List
import pytest
from main import dfs, make_results_clean


def test_graph():
    """sumary_line

    Keyword arguments:
    argument -- description
    Return: return_description
    """
    test_result: List = dfs([[0, 0, 1], [0, 0, 1], [0, 0, 0]])
    assert [[0, []], [1, []], []] == test_result

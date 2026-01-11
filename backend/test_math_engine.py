import pytest
from math_engine import evaluate_worksheet

def test_evaluate_worksheet_basic():
    regions = [
        {'id': '1', 'content': '1 + 1', 'x': 0, 'y': 0}
    ]
    results = evaluate_worksheet(regions)
    # Check approximate float value
    assert abs(float(results['1']) - 2.0) < 1e-9

def test_evaluate_worksheet_variables_scope():
    # Test top-to-bottom variable definition
    regions = [
        {'id': '1', 'content': 'a := 5', 'x': 0, 'y': 0},
        {'id': '2', 'content': 'a + 2', 'x': 0, 'y': 100}
    ]
    results = evaluate_worksheet(regions)
    assert abs(float(results['1']) - 5.0) < 1e-9
    assert abs(float(results['2']) - 7.0) < 1e-9

def test_evaluate_worksheet_variables_scope_ordering():
    # Test that defining variable BELOW usage fails (or uses old value/error)
    regions = [
        {'id': '1', 'content': 'b + 1', 'x': 0, 'y': 0},
        {'id': '2', 'content': 'b := 10', 'x': 0, 'y': 100}
    ]
    results = evaluate_worksheet(regions)
    assert "Error" in results['1']
    assert abs(float(results['2']) - 10.0) < 1e-9

def test_evaluate_worksheet_global_definition():
    # Test global definition works anywhere regardless of position
    regions = [
        {'id': '1', 'content': 'g + 5', 'x': 0, 'y': 0},
        {'id': '2', 'content': r'g \equiv 20', 'x': 0, 'y': 100}
    ]
    results = evaluate_worksheet(regions)
    assert abs(float(results['2']) - 20.0) < 1e-9
    assert abs(float(results['1']) - 25.0) < 1e-9

def test_evaluate_worksheet_latex_fractions():
    regions = [
        {'id': '1', 'content': r'\frac{1}{2}', 'x': 0, 'y': 0}
    ]
    results = evaluate_worksheet(regions)
    assert abs(float(results['1']) - 0.5) < 1e-9

def test_evaluate_worksheet_assignment_coloneq():
    regions = [
        {'id': '1', 'content': r'x \coloneq 10', 'x': 0, 'y': 0},
        {'id': '2', 'content': 'x * 2', 'x': 0, 'y': 50}
    ]
    results = evaluate_worksheet(regions)
    assert abs(float(results['2']) - 20.0) < 1e-9

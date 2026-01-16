
import pytest
from math_engine import evaluate_worksheet, parse_latex_expression
import sympy

def test_basic_math_functions():
    regions = [
        {'id': '1', 'x': 0, 'y': 0, 'content': 'sin(3.14)'},
        {'id': '2', 'x': 0, 'y': 20, 'content': 'cos(0)'},
        {'id': '3', 'x': 0, 'y': 40, 'content': r'\sqrt{4}'}, # Strict LaTeX for sqrt
        {'id': '4', 'x': 0, 'y': 60, 'content': 'log(e)'}
    ]
    results = evaluate_worksheet(regions)

    # sin(3.14) is approx 0.00159...
    if 'Error' in str(results['1']):
         pytest.fail(f"Region 1 failed: {results['1']}")
    assert abs(float(results['1']) - 0.00159) < 0.00001

    assert float(results['2']) == 1.0

    if 'Error' in str(results['3']):
         pytest.fail(f"Region 3 failed: {results['3']}")
    assert float(results['3']) == 2.0

    assert float(results['4']) == 1.0

def test_plot_parsing_with_parens():
    regions = [
        {'id': '1', 'x': 0, 'y': 0, 'content': 'plot(sin(x), x, 0, 10)'},
        {'id': '2', 'x': 0, 'y': 20, 'content': 'plot(x^2, x, -5, 5)'}
    ]
    results = evaluate_worksheet(regions)

    assert isinstance(results['1'], dict)
    assert results['1']['type'] == 'plot'
    assert len(results['1']['data']) == 100

    assert isinstance(results['2'], dict)
    assert results['2']['type'] == 'plot'
    assert len(results['2']['data']) == 100

def test_plot_parsing_error():
    regions = [
        {'id': '1', 'x': 0, 'y': 0, 'content': 'plot(sin(x), x)'} # Missing args
    ]
    results = evaluate_worksheet(regions)
    assert "Error: plot" in results['1']

def test_definitions():
    regions = [
        {'id': '1', 'x': 0, 'y': 0, 'content': 'a := 10'},
        {'id': '2', 'x': 0, 'y': 20, 'content': 'b := a + 5'}
    ]
    results = evaluate_worksheet(regions)
    assert float(results['1']) == 10.0
    assert float(results['2']) == 15.0

def test_latex_parsing_robustness():
    # Test \sin
    regions = [
        {'id': '1', 'x': 0, 'y': 0, 'content': r'\sin(3.14)'}
    ]
    results = evaluate_worksheet(regions)
    assert abs(float(results['1']) - 0.00159) < 0.00001

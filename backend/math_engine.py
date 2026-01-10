import sympy

def evaluate_expression(expression):
    try:
        # Use sympy to parse and evaluate the expression
        # sympify is powerful but we should be careful with inputs in a real app
        # For this whiteboard, we assume trusted input or basic math
        expr = sympy.sympify(expression)
        result = expr.evalf()
        return result
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")

import sympy
from sympy.parsing.latex import parse_latex
from pint import UnitRegistry, UndefinedUnitError
import re
import numpy as np

# Initialize Unit Registry
ureg = UnitRegistry()
Q_ = ureg.Quantity

def parse_latex_expression(expression_str):
    """
    Parses a LaTeX string into a SymPy expression or assignment.
    Returns a tuple: (type, name, value, is_symbolic)
    """
    expression_str = expression_str.strip()
    is_symbolic = False

    # Check for symbolic operator ->
    if r'\rightarrow' in expression_str:
        is_symbolic = True
        parts = expression_str.split(r'\rightarrow')
        expression_str = parts[0].strip()
    elif '->' in expression_str:
        is_symbolic = True
        parts = expression_str.split('->')
        expression_str = parts[0].strip()

    # Check for Global Definition (\equiv)
    if r'\equiv' in expression_str:
        parts = expression_str.split(r'\equiv')
        if len(parts) == 2:
            return ('global_definition', parts[0].strip(), parse_latex(parts[1].strip()), is_symbolic)

    # Check for Local Definition (:= or \coloneq)
    definition_op = None
    if ':=' in expression_str:
        definition_op = ':='
    elif r'\coloneq' in expression_str:
        definition_op = r'\coloneq'

    if definition_op:
        parts = expression_str.split(definition_op)
        if len(parts) == 2:
            return ('definition', parts[0].strip(), parse_latex(parts[1].strip()), is_symbolic)

    # Standard Expression
    clean_expr = expression_str
    if clean_expr.endswith('='):
        clean_expr = clean_expr[:-1]

    # Special case for plot command: plot(expr, var, start, end)
    # We use a regex because antlr latex parser might fail on 'plot'
    plot_match = re.match(r'^plot\((.*)\)$', clean_expr)
    if plot_match:
        # We'll return a special type or just the parsed content
        # For now, let's keep it as an expression but mark it
        try:
            # Try to parse the inside as a comma-separated list
            # This is tricky for nested commas, but we'll try a simple split for now
            # or just return the whole thing and handle it in evaluation
            return ('plot', None, clean_expr, is_symbolic)
        except:
            pass

    return ('expression', None, parse_latex(clean_expr), is_symbolic)

def evaluate_worksheet(regions):
    """
    Evaluates a list of regions based on position and scope.
    """
    symbol_table = {
        'pi': sympy.pi,
        'e': sympy.E,
        'g': 9.80665
    }
    
    results = {}
    parsed_regions = []

    for region in regions:
        try:
            rtype, rname, rexpr, rsymb = parse_latex_expression(region['content'])
            parsed_regions.append({
                'id': region['id'],
                'x': region['x'],
                'y': region['y'],
                'type': rtype,
                'name': rname,
                'expr': rexpr,
                'symbolic': rsymb
            })
        except Exception as e:
            results[region['id']] = f"Error: {str(e)}"

    parsed_regions.sort(key=lambda r: (0 if r['type'] == 'global_definition' else 1, r['y'], r['x']))

    for r in parsed_regions:
        try:
            # Handle Plot Type specifically
            if r['type'] == 'plot':
                content = r['expr'] # This is the full 'plot(expr, var, start, end)' string
                # Extract args more carefully
                args_str = content[5:-1]
                # Split by comma but respect parentheses (naive)
                # Better: find the 4 segments
                # For now, we expect simple plot(x^2, x, 0, 10)
                args = [s.strip() for s in args_str.split(',')]
                if len(args) == 4:
                    func_expr = parse_latex(args[0])
                    var = sympy.Symbol(args[1])
                    start = float(parse_latex(args[2]).evalf())
                    end = float(parse_latex(args[3]).evalf())
                    
                    x_vals = np.linspace(start, end, 100)
                    # Use subs to resolve other variables in function
                    f_ready = func_expr.subs(symbol_table)
                    f = sympy.lambdify(var, f_ready, "numpy")
                    y_vals = f(x_vals)
                    
                    # Handle if y_vals is a single number (constant function)
                    if np.isscalar(y_vals):
                        y_vals = np.full_like(x_vals, y_vals)
                    
                    results[r['id']] = {
                        'type': 'plot',
                        'data': [{'x': float(x), 'y': float(y)} for x, y in zip(x_vals, y_vals)]
                    }
                    continue
                else:
                    results[r['id']] = "Error: plot(expr, var, start, end)"
                    continue

            expr = r['expr']
            current_val = expr.subs(symbol_table)
            
            if r['symbolic']:
                res = sympy.simplify(current_val)
                result_str = str(res)
            else:
                res = current_val.evalf()
                if res.is_number:
                    result_str = f"{float(res):.4g}"
                else:
                    if res.free_symbols:
                        result_str = f"Error: Undefined {res.free_symbols}"
                    else:
                        result_str = str(res)

            if r['type'] in ['definition', 'global_definition']:
                lhs_symbol = parse_latex(r['name'])
                symbol_table[lhs_symbol] = res
                results[r['id']] = result_str
            else:
                results[r['id']] = result_str

        except Exception as e:
            results[r['id']] = f"Error: {str(e)}"

    return results

def evaluate_expression(expression):
    try:
        expr = sympy.sympify(expression)
        return expr.evalf()
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")

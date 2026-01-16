import sympy
from sympy.parsing.latex import parse_latex
from pint import UnitRegistry, UndefinedUnitError
import re
import numpy as np

# Initialize Unit Registry
ureg = UnitRegistry()
Q_ = ureg.Quantity

# Base Symbol Table
# Note: sympy.sqrt is a function, not a FunctionClass. This causes issues with sympify in subs.
# We should not put raw python functions in the symbol table if we intend to use them in subs directly
# unless we wrap them or they are supported.
# However, standard functions like sin, cos are FunctionClasses.
# For sqrt, we might rely on the parser to produce 'sqrt' function call if preprocessed to \sqrt.
# If we have 'sqrt' in the text, it becomes Symbol('sqrt').
# We can't sub Symbol('sqrt') with a python function.
# But \sqrt parses to a Power object (x**0.5).

BASE_SYMBOL_TABLE = {
    'pi': sympy.pi,
    'e': sympy.E,
    'g': 9.80665,
    'sin': sympy.sin,
    'cos': sympy.cos,
    'tan': sympy.tan,
    # 'sqrt': sympy.sqrt,  <-- Removed to avoid SympifyError
    'log': sympy.log,
    'ln': sympy.ln,
    'exp': sympy.exp,
    'abs': sympy.Abs
}

def preprocess_latex(latex_str):
    """
    Converts standard math function names to LaTeX commands.
    e.g. 'sin(x)' -> '\\sin(x)'
    """
    # List of functions to convert
    # Removed sqrt because \sqrt requires braces {}, not parens.
    funcs = ['sin', 'cos', 'tan', 'log', 'ln', 'exp']

    # We use regex to replace whole words only, not preceded by backslash
    for func in funcs:
        # Pattern: lookbehind for no backslash, lookboundary, word, lookboundary
        # Python re doesn't support variable length lookbehind easily, but we can do:
        # (?:^|[^\\])\bfunc\b -> but we need to preserve the char before.
        # Simpler: replace \bfunc\b with \func, then fix double backslashes if any?
        # Or just use positive lookbehind if the pattern is fixed length? No.

        # We want to match ' sin ' or '(sin' or 'sin('.
        # Regex: (?<!\\)\b(sin|cos|...)\b
        pattern = r'(?<!\\)\b' + func + r'\b'
        latex_str = re.sub(pattern, r'\\' + func, latex_str)

    return latex_str

def parse_plot_args(args_str):
    """
    Parses comma-separated arguments, respecting nested parentheses.
    """
    args = []
    current = []
    depth = 0

    for char in args_str:
        if char == ',' and depth == 0:
            args.append("".join(current).strip())
            current = []
        else:
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            current.append(char)

    if current:
        args.append("".join(current).strip())

    return args

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
    if clean_expr.startswith('plot(') and clean_expr.endswith(')'):
        return ('plot', None, clean_expr, is_symbolic)

    return ('expression', None, parse_latex(clean_expr), is_symbolic)

def evaluate_worksheet(regions):
    """
    Evaluates a list of regions based on position and scope.
    """
    symbol_table = BASE_SYMBOL_TABLE.copy()
    
    results = {}
    parsed_regions = []

    for region in regions:
        try:
            # Preprocess content (handled carefully)
            preprocessed_content = preprocess_latex(region['content'])

            rtype, rname, rexpr, rsymb = parse_latex_expression(preprocessed_content)
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
                # Extract args
                # content looks like "plot(..., ..., ..., ...)"
                # We strip "plot(" and ")"
                args_str = content[5:-1]

                args = parse_plot_args(args_str)

                if len(args) == 4:
                    # Note: args[0] is part of the preprocessed string, so it should be valid latex if preprocess worked.
                    func_expr = parse_latex(args[0])
                    var = sympy.Symbol(args[1])
                    start = float(parse_latex(args[2]).evalf())
                    end = float(parse_latex(args[3]).evalf())
                    
                    x_vals = np.linspace(start, end, 100)

                    # Resolve symbols
                    f_ready = func_expr.subs(symbol_table)

                    # Lambdify
                    f = sympy.lambdify(var, f_ready, "numpy")
                    y_vals = f(x_vals)
                    
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
            
            # Substitute symbols from table
            try:
                current_val = expr.subs(symbol_table)
            except Exception as e:
                # Fallback or pass
                current_val = expr

            if r['symbolic']:
                res = sympy.simplify(current_val)
                result_str = str(res)
            else:
                res = current_val.evalf()
                if res.is_number:
                    result_str = f"{float(res):.4g}"
                else:
                    # check if free symbols remain
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

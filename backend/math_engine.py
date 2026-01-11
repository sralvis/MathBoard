import sympy
from sympy.parsing.latex import parse_latex

def parse_latex_expression(expression_str):
    """
    Parses a LaTeX string into a SymPy expression or assignment.
    Returns a tuple: (type, name, value)
    type: 'definition' or 'expression' or 'global_definition'
    name: variable name (if definition), else None
    value: SymPy expression object
    """
    expression_str = expression_str.strip()

    # Check for Global Definition (\equiv)
    if r'\equiv' in expression_str:
        parts = expression_str.split(r'\equiv')
        if len(parts) == 2:
            lhs = parts[0].strip()
            rhs = parts[1].strip()
            return ('global_definition', lhs, parse_latex(rhs))

    # Check for Local Definition (:= or \coloneq)
    definition_op = None
    if ':=' in expression_str:
        definition_op = ':='
    elif r'\coloneq' in expression_str:
        definition_op = r'\coloneq'

    if definition_op:
        parts = expression_str.split(definition_op)
        if len(parts) == 2:
            lhs = parts[0].strip()
            rhs = parts[1].strip()
            return ('definition', lhs, parse_latex(rhs))

    # Standard Expression
    clean_expr = expression_str
    if clean_expr.endswith('='):
        clean_expr = clean_expr[:-1]

    return ('expression', None, parse_latex(clean_expr))

def evaluate_worksheet(regions):
    """
    Evaluates a list of regions based on position and scope.
    regions: List of dicts {id, content, x, y}
    Returns: Dict {id: result_string}
    """
    symbol_table = {}
    results = {}

    # Helper to safe evaluate
    def safe_eval(expr, symbols):
        try:
            # subs all symbols
            res = expr.evalf(subs=symbols)
            # Check if result still has free symbols (meaning undefined variables were used)
            if res.free_symbols:
                return "Error: Undefined Variable"
            return res
        except Exception:
            return "Error"

    parsed_regions = []

    # Parse all regions first
    for region in regions:
        try:
            rtype, rname, rexpr = parse_latex_expression(region['content'])
            parsed_regions.append({
                'id': region['id'],
                'x': region['x'],
                'y': region['y'],
                'type': rtype,
                'name': rname,
                'expr': rexpr
            })
        except Exception as e:
            results[region['id']] = "Error"

    # Pass 1: Global Definitions
    globals_list = [r for r in parsed_regions if r['type'] == 'global_definition']
    globals_list.sort(key=lambda r: (r['y'], r['x']))

    for r in globals_list:
        try:
            val = safe_eval(r['expr'], symbol_table)
            if str(val).startswith("Error"):
                results[r['id']] = val
            else:
                symbol_table[parse_latex(r['name'])] = val
                results[r['id']] = str(val)
        except Exception as e:
            results[r['id']] = "Error"

    # Pass 2 & 3: Local Definitions and Expressions
    locals_list = [r for r in parsed_regions if r['type'] != 'global_definition']
    locals_list.sort(key=lambda r: (r['y'], r['x']))

    for r in locals_list:
        if r['type'] == 'definition':
            try:
                val = safe_eval(r['expr'], symbol_table)
                if str(val).startswith("Error"):
                    results[r['id']] = val
                else:
                    symbol_table[parse_latex(r['name'])] = val
                    results[r['id']] = str(val)
            except Exception:
                results[r['id']] = "Error"
        elif r['type'] == 'expression':
            try:
                val = safe_eval(r['expr'], symbol_table)
                results[r['id']] = str(val)
            except Exception:
                results[r['id']] = "Error"

    return results

def evaluate_expression(expression):
    try:
        expr = sympy.sympify(expression)
        return expr.evalf()
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")

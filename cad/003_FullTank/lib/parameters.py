"""Restricted, dimension-aware arithmetic for reconstruction parameters."""
import ast
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Quantity:
    value: float
    dimension: tuple = (0, 0)  # powers of millimeters and degrees


UNITS = {"mm": (1.0, (1, 0)), "in": (25.4, (1, 0)), "deg": (1.0, (0, 1)),
         "count": (1.0, (0, 0)), "scalar": (1.0, (0, 0)),
         "mm2": (1.0, (2, 0)), "mm3": (1.0, (3, 0))}


def evaluate(expression, values):
    if type(expression) in (int, float):
        return Quantity(float(expression))
    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return Quantity(float(node.value))
        if isinstance(node, ast.Name):
            if node.id not in values:
                raise ValueError("Unknown parameter: " + node.id)
            return values[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            q = visit(node.operand)
            return Quantity(q.value * (-1 if isinstance(node.op, ast.USub) else 1), q.dimension)
        if isinstance(node, ast.BinOp):
            a, b = visit(node.left), visit(node.right)
            if isinstance(node.op, (ast.Add, ast.Sub)):
                if a.dimension != b.dimension:
                    raise ValueError("Dimension mismatch in " + expression)
                return Quantity(a.value + (b.value if isinstance(node.op, ast.Add) else -b.value), a.dimension)
            if isinstance(node.op, ast.Mult):
                return Quantity(a.value*b.value, tuple(x+y for x, y in zip(a.dimension,b.dimension)))
            if isinstance(node.op, ast.Div):
                return Quantity(a.value/b.value, tuple(x-y for x, y in zip(a.dimension,b.dimension)))
        raise ValueError("Unsupported parameter expression: " + str(expression))
    result = visit(ast.parse(expression, mode="eval").body)
    if not math.isfinite(result.value):
        raise ValueError("Nonfinite parameter expression")
    return result


def resolve(records):
    values, visiting = {}, set()
    def one(key):
        if key in values:
            return values[key]
        if key in visiting:
            raise ValueError("Parameter dependency cycle: " + key)
        if key not in records:
            raise ValueError("Missing parameter: " + key)
        visiting.add(key)
        item = records[key]
        if item.get("blocked"):
            raise ValueError("Unresolved parameter conflict: " + key)
        if item["unit"] not in UNITS:
            raise ValueError("Unknown units for " + key)
        scale, dimension = UNITS[item["unit"]]
        if "expression" in item:
            node = ast.parse(item["expression"], mode="eval")
            for name in {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}:
                one(name)
            q = evaluate(item["expression"], values)
            if q.dimension != dimension:
                raise ValueError("Wrong expression units for " + key)
        else:
            if type(item["value"]) not in (int, float):
                raise ValueError("Parameter value must be numeric: " + key)
            q = Quantity(float(item["value"])*scale, dimension)
        if not math.isfinite(q.value):
            raise ValueError("Nonfinite value: " + key)
        lo, hi = item["bounds"]
        if not all(math.isfinite(x) for x in [lo,hi]) or not lo*scale <= q.value <= hi*scale:
            raise ValueError("Value outside reconstruction bounds: " + key)
        if item["unit"] == "count" and (q.value < 0 or q.value != int(q.value)):
            raise ValueError("Count must be a nonnegative integer: " + key)
        visiting.remove(key)
        values[key] = q
        return q
    for key in records:
        one(key)
    return values


def scalar(expression, values, dimension=(1,0)):
    # Literal coordinates use the unit declared by the enclosing geometry field.
    q = Quantity(float(expression), dimension) if type(expression) in (int,float) else evaluate(expression,values)
    if q.dimension != dimension or not math.isfinite(q.value):
        raise ValueError("Invalid geometry-field units/value: " + str(expression))
    return q.value

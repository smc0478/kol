from __future__ import annotations
from enum import Enum, auto

def _ast_repr(obj, indent=0):
    """Helper function for pretty-printing AST nodes."""
    if isinstance(obj, AST):
        return obj.__repr__(indent)
    if isinstance(obj, list):
        items = ',\n'.join([_ast_repr(item, indent + 1) for item in obj])
        return f'[\n{items}\n' + '  ' * indent + ']'
    if isinstance(obj, dict):
        items = ',\n'.join([f"{'  ' * (indent + 1)}{_ast_repr(k, 0)}: {_ast_repr(v, indent + 1)}" for k, v in obj.items()])
        return f'{{\n{items}\n' + '  ' * indent + '}}'
    return repr(obj)

class AST:
    _next_id_ = 0
    def __init__(self):
        self.ast_id = self._next_id_
        self._next_id_ += 1


class StmtAST(AST):
    pass

class ExprAST(AST):
    pass

def _repr_maker(name, fields):
    def __repr__(self, indent=0):
        indent_str = '  ' * indent
        field_strs = []
        for field in fields:
            value = getattr(self, field)
            value_repr = _ast_repr(value, indent + 1)
            field_strs.append(f"\n{'  ' * (indent + 1)}{field}={value_repr}")
        
        return f"{indent_str}{name}({''.join(field_strs)}\n{indent_str})"
    return __repr__


class ProgramAST(AST):
    def __init__(self, body: BodyAST):
        super().__init__()
        self.body = body
    __repr__ = _repr_maker("ProgramAST", ["body"])

class BodyAST(StmtAST):
    def __init__(self, stmts:list[StmtAST]):
        super().__init__()
        self.stmts = stmts
    __repr__ = _repr_maker("BodyAST", ["stmts"])

class StructAST(StmtAST):
    def __init__(self, ident: str, vars: list[str]):
        super().__init__()
        self.ident = ident
        self.vars = vars
    __repr__ = _repr_maker("StructAST", ["ident", "vars"])

class ClassAST(StmtAST):
    def __init__(self, ident: str, vars: list[str], 
                funcs: list[FuncAST], parent: str|None, initial: FuncAST|None):
        super().__init__()
        self.ident = ident
        self.vars = vars
        self.funcs = funcs
        self.parent = parent
        self.initial = initial
    __repr__ = _repr_maker("ClassAST", ["ident", "vars", "funcs", "parent", "initial"])

class FuncAST(StmtAST):
    def __init__(self, ident: str, params: list[str],
                    body: BodyAST):
        super().__init__()
        self.ident = ident
        self.params = params
        self.body = body
    __repr__ = _repr_maker("FuncAST", ["ident", "params", "body"])

class WhileAST(StmtAST):
    def __init__(self, cond: ExprAST, body: BodyAST):
        super().__init__()
        self.cond = cond
        self.body = body
    __repr__ = _repr_maker("WhileAST", ["cond", "body"])
        
class ForAST(StmtAST):
    def __init__(self, iter: ExprAST, ident: str, body: BodyAST):
        super().__init__()
        self.iter = iter
        self.ident = ident
        self.body = body
    __repr__ = _repr_maker("ForAST", ["iter", "ident", "body"])

class CondAST(StmtAST):
    def __init__(self, cond: ExprAST, then_body: BodyAST, else_cond: CondAST|None):
        super().__init__()
        self.cond = cond
        self.then_body = then_body
        self.else_cond = else_cond
    __repr__ = _repr_maker("CondAST", ["cond", "then_body", "else_cond"])

class ContinueAST(StmtAST):
    def __init__(self):
        super().__init__()
    def __repr__(self, indent=0): return f"{'  ' * indent}ContinueAST()"

class BreakAST(StmtAST):
    def __init__(self):
        super().__init__()
    def __repr__(self, indent=0): return f"{'  ' * indent}BreakAST()"

class ReturnAST(StmtAST):
    def __init__(self, value: ExprAST):
        super().__init__()
        self.value = value
    __repr__ = _repr_maker("ReturnAST", ["value"])

class AssignAST(StmtAST):
    def __init__(self, lvalue: ExprAST, rvalue: ExprAST):
        super().__init__()
        self.lvalue = lvalue
        self.rvalue = rvalue
    __repr__ = _repr_maker("AssignAST", ["lvalue", "rvalue"])

class CallStmtAST(StmtAST):
    def __init__(self, callee: ExprAST, params: list[ExprAST] = []):
        super().__init__()
        self.callee = callee
        self.params = params
    __repr__ = _repr_maker("CallStmtAST", ["callee", "params"])

class ExprStmtAST(StmtAST):
    def __init__(self, expr: ExprAST):
        super().__init__()
        self.expr = expr
    __repr__ = _repr_maker("ExprStmtAST", ["expr"])

class BinAST(ExprAST):
    class OpKind(Enum):
        OP_AND = auto()
        OP_OR = auto()
        OP_EQUAL = auto()
        OP_NOTEQUAL = auto()
        OP_LIKE = auto()
        OP_NOTLIKE = auto()
        OP_GE = auto()
        OP_GT = auto()
        OP_LE = auto()
        OP_LT = auto()
        OP_SHL = auto()
        OP_SHR = auto()

    def __init__(self, op: OpKind, left: ExprAST, right: ExprAST):
        super().__init__()
        self.op = op
        self.left = left
        self.right = right
    __repr__ = _repr_maker("BinAST", ["op", "left", "right"])

class FieldAccessAST(ExprAST):
    def __init__(self, target: ExprAST, field: str):
        super().__init__()
        self.target = target
        self.field = field
    __repr__ = _repr_maker("FieldAccessAST", ["target", "field"])
    
class MethodAccessAST(ExprAST):
    def __init__(self, target: ExprAST, method: str):
        super().__init__()
        self.target = target
        self.method = method
    __repr__ = _repr_maker("MethodAccessAST", ["target", "method"])

class IndexAccessAST(ExprAST):
    def __init__(self, target: ExprAST, idx: ExprAST):
        super().__init__()
        self.target = target
        self.idx = idx
    __repr__ = _repr_maker("IndexAccessAST", ["target", "idx"])


class CallExprAST(ExprAST):
    def __init__(self, callee: ExprAST, params: list[ExprAST] = []):
        super().__init__()
        self.callee = callee
        self.params = params
    __repr__ = _repr_maker("CallExprAST", ["callee", "params"])

class IntegerAST(ExprAST):
    def __init__(self, num: int):
        super().__init__()
        self.num = num
    def __repr__(self, indent=0): return f"{'  ' * indent}IntegerAST({self.num!r})"

class FloatAST(ExprAST):
    def __init__(self, num: float):
        super().__init__()
        self.num = num
    def __repr__(self, indent=0): return f"{'  ' * indent}FloatAST({self.num!r})"

class StringAST(ExprAST):
    def __init__(self, str: str):
        super().__init__()
        self.str = str
    def __repr__(self, indent=0): return f"{'  ' * indent}StringAST({self.str!r})"

class BoolAST(ExprAST):
    def __init__(self, value: bool):
        super().__init__()
        self.value = value
    def __repr__(self, indent=0): return f"{'  ' * indent}BoolAST({self.value!r})"

class IdentifierAST(ExprAST):
    def __init__(self, ident: str):
        super().__init__()
        self.ident = ident
    def __repr__(self, indent=0): return f"{'  ' * indent}IdentifierAST({self.ident!r})"

class DictAST(ExprAST):
    def __init__(self, dict_values: dict = {}):
        super().__init__()
        self.dict_values = dict_values
    __repr__ = _repr_maker("DictAST", ["dict_values"])

class ArrayAST(ExprAST):
    def __init__(self, elems: list = []):
        super().__init__()
        self.elems = elems
    __repr__ = _repr_maker("ArrayAST", ["elems"])


class NoneAST(ExprAST):
    def __init__(self):
        super().__init__()
    def __repr__(self, indent=0): return f"{'  ' * indent}NoneAST()"

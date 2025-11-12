from .ast import FuncAST
import types
function = types.FunctionType

class Func:
    def __init__(self, ast_or_pyfunc: FuncAST|function, 
                 global_scope: dict = {}, class_scope: dict = {},
                 params_count = -1):
        self.code: FuncAST|list|function = ast_or_pyfunc
        self.current_scope = global_scope
        self.class_scope = class_scope
        if isinstance(ast_or_pyfunc, FuncAST):
            self.args = ast_or_pyfunc.params
        else:
            self.args = [None]*params_count
        self.local_count = 0

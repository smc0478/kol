from .ast import *
from .bytecode import *
from .func import Func
from .struct import Struct, Class
from .builtin import builtins

class Compiler:
    def __init__(self, global_scope:dict = {}, const_pool:list = [], 
                 class_scope: dict = {}):
        self.scope = {}
        self.global_scope = global_scope
        self.bytecode = []
        self.class_scope = class_scope
        self.const_pool = const_pool
        self.cont_binds = []
        self.brek_binds = []
        self.visit_map = {
            ProgramAST: self.visit_program,
            BodyAST: self.visit_body,
            StructAST: self.visit_struct,
            ClassAST: self.visit_class,
            FuncAST: self.visit_func,
            WhileAST: self.visit_while,
            ForAST: self.visit_for,
            CondAST: self.visit_cond,
            ContinueAST: self.visit_continue,
            BreakAST: self.visit_break,
            ReturnAST: self.visit_return,
            AssignAST: self.visit_assign,
            CallStmtAST: self.visit_call_stmt,
            CallExprAST: self.visit_call_expr,
            ExprStmtAST: self.visit_expr_stmt,
            BinAST: self.visit_bin,
            FieldAccessAST: self.visit_field_access,
            MethodAccessAST: self.visit_method_access,
            IndexAccessAST: self.visit_index_access,
            IntegerAST: self.visit_number,
            FloatAST: self.visit_number,
            StringAST: self.visit_string,
            BoolAST: self.visit_bool,
            NoneAST: self.visit_none,
            DictAST: self.visit_dict,
            ArrayAST: self.visit_array,
            IdentifierAST: self.visit_identifier,
        }
        self.is_global = False
        self.assign = 0

    def get_global_scope(self):
        if self.is_global:
            return self.scope
        else:
            return self.global_scope

    @staticmethod
    def compile_func(func: Func, const_pool):
        compiler = Compiler(func.current_scope, const_pool, func.class_scope)
        compiler.do_compile_func(func.args, func.code.body)
        func.code = compiler.bytecode
        func.local_count = compiler.assign

    def do_compile_func(self, args: list, body: BodyAST):
        self.assign = len(args)
        for i,arg in enumerate(args):
            self.scope[arg] = i
        self.visit(body)
        if not isinstance(self.bytecode[-1], Ret):
            self.bytecode.append(LoadConst(None))
            self.bytecode.append(Ret())

    def compile_main(self, ast):
        self.assign = len(builtins)
        for i, ident in enumerate(builtins):
            self.scope[ident] = i        
        self.visit(ast)

    def visit(self, ast):
        self.visit_map[type(ast)](ast)

    def visit_program(self, ast: ProgramAST):
        self.is_global = True
        self.visit(ast.body)

    def visit_body(self, ast: BodyAST):
        for stmt in ast.stmts:
            self.visit(stmt)

    def visit_struct(self, ast: StructAST):
        if ast.ident not in self.scope:
            self.scope[ast.ident] = self.assign
            self.assign += 1

        self.class_scope[ast.ident] = len(self.const_pool)
        self.bytecode.append(StoreFromConstPool(
            len(self.const_pool), self.scope[ast.ident]))
        self.const_pool.append(Struct(ast.vars))
    
    def visit_class(self, ast: ClassAST):
        if ast.ident not in self.scope:
            self.scope[ast.ident] = self.assign
            self.assign += 1

        funcs = {}
        for func_ast in ast.funcs:
            funcs[func_ast.ident] = Func(func_ast, self.scope|self.global_scope, 
                                         class_scope=self.class_scope)

        self.class_scope[ast.ident] = len(self.const_pool)
        self.bytecode.append(StoreFromConstPool(
            len(self.const_pool), self.scope[ast.ident]))

        parent = self.class_scope.get(ast.parent, None)
        if parent:
            parent = self.const_pool[parent]
        self.const_pool.append(Class(ast.vars, funcs, parent))
        
    def visit_func(self, ast: FuncAST):
        if ast.ident not in self.scope:
            self.scope[ast.ident] = self.assign
            self.assign += 1

        self.bytecode.append(StoreFromConstPool(
            len(self.const_pool), self.scope[ast.ident]))
        self.const_pool.append(Func(ast, self.scope|self.global_scope,
                                    class_scope=self.class_scope))
        if ast.ident in self.class_scope:
            self.class_scope.pop(ast.ident)

    def visit_while(self, ast: WhileAST):
        tmp_cont, tmp_brek = self.cont_binds, self.brek_binds
        self.cont_binds, self.brek_binds = [], []
        repeat_ip = len(self.bytecode)
        self.visit(ast.cond)
        end = self.label()
        self.bytecode.append(JmpIfFalse())
        self.visit(ast.body)
        self.bytecode.append(Jmp(repeat_ip))
        self.bind(end)
        self.loop_finish(repeat_ip, len(self.bytecode))
        self.cont_binds, self.brek_binds = tmp_cont, tmp_brek

    def visit_for(self, ast: ForAST):
        tmp_cont, tmp_brek = self.cont_binds, self.brek_binds
        self.cont_binds, self.brek_binds = [], []
        self.scope[ast.ident] = self.assign
        self.assign += 1
        self.visit(ast.iter)
        self.bytecode.append(ForInPrepare())
        repeat_ip = len(self.bytecode)
        self.bytecode.append(ForInStep(self.scope[ast.ident]))
        end = self.label()
        self.bytecode.append(JmpIfFalse())
        self.visit(ast.body)
        self.bytecode.append(Jmp(repeat_ip))
        self.bind(end)
        self.loop_finish(repeat_ip, len(self.bytecode))
        self.bytecode.append(ForInDone())
        self.cont_binds, self.brek_binds = tmp_cont, tmp_brek

    def visit_cond(self, ast: CondAST):
        self.visit(ast.cond)
        else_cond = self.label()
        self.bytecode.append(JmpIfFalse())
        self.visit(ast.then_body)
        if ast.else_cond:
            end = self.label()
            self.bytecode.append(Jmp())
            self.bind(else_cond)
            self.visit(ast.else_cond)
            self.bind(end)
        else:
            self.bind(else_cond)

    def visit_continue(self, ast: ContinueAST):
        self.cont_binds.append(len(self.bytecode))
        self.bytecode.append(Jmp())

    def visit_break(self, ast: BreakAST):
        self.brek_binds.append(len(self.bytecode))
        self.bytecode.append(Jmp())

    def visit_return(self, ast: ReturnAST):
        self.visit(ast.value)
        self.bytecode.append(Ret())

    def visit_assign(self, ast: AssignAST):
        if isinstance(ast.lvalue, IdentifierAST) and \
            ast.lvalue.ident not in self.scope:
            self.scope[ast.lvalue.ident] = self.assign
            self.assign += 1
        
        self.visit(ast.rvalue)
        if isinstance(ast.lvalue, IdentifierAST) and self.is_global:
            self.bytecode.append(
                StoreGlobal(self.scope[ast.lvalue.ident]))
            if ast.lvalue.ident in self.class_scope:
                self.class_scope.pop(ast.lvalue.ident)
        elif isinstance(ast.lvalue, IdentifierAST) and not self.is_global:
            self.bytecode.append(
                StoreLocal(self.scope[ast.lvalue.ident]))
            if ast.lvalue.ident in self.class_scope:
                self.class_scope.pop(ast.lvalue.ident)
        elif isinstance(ast.lvalue, FieldAccessAST):
            self.visit(ast.lvalue.target)
            self.bytecode.append(StoreField(ast.lvalue.field))
        elif isinstance(ast.lvalue, IndexAccessAST):
            self.visit(ast.lvalue.target)
            self.visit(ast.lvalue.idx)
            self.bytecode.append(StoreIndex())
        else:
            raise Exception("문법 에러: 왼쪽 값이 문제있음")

    def visit_expr_stmt(self, ast: ExprStmtAST):
        self.visit(ast.expr)
        self.bytecode.append(Pop())

    def visit_bin(self, ast: BinAST):
        if ast.op == BinAST.OpKind.OP_AND:
            self.visit(ast.left)
            left_false = self.label()
            self.bytecode.append(JmpIfFalse())
            self.visit(ast.right)
            right_false = self.label()
            self.bytecode.append(JmpIfFalse())
            self.bytecode.append(LoadConst(True))
            end = self.label()
            self.bytecode.append(Jmp())
            self.bind(left_false)
            self.bind(right_false)
            self.bytecode.append(LoadConst(False))
            self.bind(end)
        elif ast.op == BinAST.OpKind.OP_OR:
            self.visit(ast.left)
            left_true = self.label()
            self.bytecode.append(JmpIfTrue())
            self.visit(ast.right)
            right_true = self.label()
            self.bytecode.append(JmpIfTrue())
            self.bytecode.append(LoadConst(False))
            end = self.label()
            self.bytecode.append(Jmp())
            self.bind(left_true)
            self.bind(right_true)
            self.bytecode.append(LoadConst(True))
            self.bind(end)
        else:
            self.visit(ast.left)
            self.visit(ast.right)
            match ast.op:
                case BinAST.OpKind.OP_EQUAL:
                    self.bytecode.append(EqualOp())
                case BinAST.OpKind.OP_NOTEQUAL:
                    self.bytecode.append(NotEqualOp())
                case BinAST.OpKind.OP_LIKE:
                    self.bytecode.append(LikeOp())
                case BinAST.OpKind.OP_NOTLIKE:
                    self.bytecode.append(NotLikeOp())
                case BinAST.OpKind.OP_GT:
                    self.bytecode.append(GTOp())
                case BinAST.OpKind.OP_GE:
                    self.bytecode.append(GEOp())
                case BinAST.OpKind.OP_LT:
                    self.bytecode.append(LTOp())
                case BinAST.OpKind.OP_LE:
                    self.bytecode.append(LEOp())
                case BinAST.OpKind.OP_SHL:
                    self.bytecode.append(SHLOp())
                case BinAST.OpKind.OP_SHR:
                    self.bytecode.append(SHROp())

    def visit_field_access(self, ast: FieldAccessAST):
        self.visit(ast.target)
        self.bytecode.append(LoadField(ast.field))

    def visit_method_access(self, ast: MethodAccessAST):
        self.visit(ast.target)
        self.bytecode.append(LoadMethod(ast.method.ident))

    def visit_index_access(self, ast: IndexAccessAST):
        self.visit(ast.target)
        self.visit(ast.idx)
        self.bytecode.append(LoadIndex())

    def visit_call_expr(self, ast: CallExprAST):
        param_count = 0
        if isinstance(ast.callee, MethodAccessAST):
            self.visit(ast.callee.target)
            param_count += 1
        for arg in ast.params:
            self.visit(arg)
            param_count += 1
        
        self.visit(ast.callee)
        self.bytecode.append(Call(param_count))

    def visit_call_stmt(self, ast: CallStmtAST):
        param_count = 0
        if isinstance(ast.callee, MethodAccessAST):
            self.visit(ast.callee.target)
            param_count += 1
        for arg in ast.params:
            self.visit(arg)
            param_count += 1
        self.visit(ast.callee)
        self.bytecode.append(Call(param_count))
        self.bytecode.append(Pop())
        self.bytecode.append(LoadConst(None))

    def visit_number(self, ast: IntegerAST|FloatAST):
        self.bytecode.append(LoadConst(ast.num))

    def visit_string(self, ast: StringAST):
        self.bytecode.append(LoadConst(ast.str))

    def visit_bool(self, ast: BoolAST):
        self.bytecode.append(LoadConst(ast.value))

    def visit_array(self, ast: ArrayAST):
        for elem in ast.elems:
            self.visit(elem)
        self.bytecode.append(BuildArray(len(ast.elems)))


    def visit_dict(self, ast: DictAST):
        for key in ast.dict_values:
            self.visit(key)
            self.visit(ast.dict_values[key])
        self.bytecode.append(BuildDict(len(ast.dict_values)))

    def visit_none(self, ast: NoneAST):
        self.bytecode.append(LoadConst(None))

    def visit_identifier(self, ast: IdentifierAST):
        if self.is_global:
            self.bytecode.append(LoadGlobal(self.scope[ast.ident]))
        elif ast.ident in self.scope:
            self.bytecode.append(LoadLocal(self.scope[ast.ident]))
        else:
            self.bytecode.append(LoadGlobal(self.global_scope[ast.ident]))


    def loop_finish(self, cont_bind, brek_bind):
        for cont in self.cont_binds:
            self.bind(cont, cont_bind)
        for brek in self.brek_binds:
            self.bind(brek, brek_bind)

    def bind(self, index: int, pos=None):
        if not pos:
            pos = len(self.bytecode)
        self.bytecode[index].bind(pos)

    def label(self):
        return len(self.bytecode)
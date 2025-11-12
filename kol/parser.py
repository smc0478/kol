from .lexer import Lexer
from .token import TokenKind, Token
from .ast import *

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.is_loop = False

    def parse(self) -> ProgramAST:
        body: BodyAST = self.parse_body(end=TokenKind.ENDOFFILE)
        return ProgramAST(body)

    def parse_body(self, end: TokenKind) -> BodyAST:
        stmts: list[StmtAST] = []
        while self.current() != end and self.current() != TokenKind.ENDOFFILE:
            stmts.append(self.parse_stmt())
        if self.current() != end:
            raise Exception("문법 에러: 문단이 안 끝남")
        return BodyAST(stmts)

    def parse_stmt(self) -> StmtAST:
        match self.current():
            case TokenKind.STRUCT:
                return self.parse_struct()
            case TokenKind.TYPE:
                return self.parse_class()
            case TokenKind.FUNC:
                return self.parse_func()
            case TokenKind.CONT:
                if self.peek() == TokenKind.HANDA:
                    if not self.is_loop:
                        raise Exception("문법 에러: 반복문에서만 계속한다.를 쓸 수 있음")
                    self.next()
                    self.next()
                    self.expect(TokenKind.DOT, "문법 에러: 문장이 끝나면 마침표를 붙여야함")
                    return ContinueAST()
                else:
                    return self.parse_while()
            case TokenKind.BREK:
                if not self.is_loop:
                    raise Exception("문법 에러: 반복문에서만 나간다.를 쓸 수 있음")
                self.next()

                self.expect(TokenKind.DA, "문법 에러: 나간다. 가 필요함")
                self.expect(TokenKind.DOT, "문법 에러: 나간다. 가 필요함")
                return BreakAST()
            case TokenKind.IF:
                return self.parse_if()
            case TokenKind.RESULT:
                self.next()
                self.expect(TokenKind.VALUE,"문법 에러: 값이 필요함")
                if self.check(TokenKind.UPSI):
                    ret = NoneAST()
                else:
                    self.expect(TokenKind.EUN, "문법 에러: 은 조사가 필요함")
                    ret = self.parse_expr()
                    self.expect(TokenKind.KA, "문법 에러: 이/가 조사가 필요함")
                    self.expect_seq(TokenKind.BECOME, TokenKind.DA, 
                                    TokenKind.DOT ,msg="문법 에러: 된다.가 필요함")
                    self.expect(TokenKind.AND, "문법 에러: 그리고가 필요함")
                self.expect_seq(TokenKind.FINISH, TokenKind.DA,
                    TokenKind.DOT, msg="문법 에러: 끝난다.가 필요함")
                return ReturnAST(ret)
            case _:
                expr: ExprAST = self.parse_expr()
                if self.check(TokenKind.EUN):
                    rvalue: ExprAST = self.parse_expr()
                    self.expect(TokenKind.KA, "문법 에러: 이/가가 필요함")
                    self.expect_seq(TokenKind.BECOME, TokenKind.DA, TokenKind.DOT, 
                                    msg="문법 에러: 된다.로 끝나야함")
                    return AssignAST(expr, rvalue)
                elif self.current() == TokenKind.E:
                    return self.parse_for(expr)
                else:
                    self.expect(TokenKind.DOT, "문법 에러: 마침표가 필요함")
                    return ExprStmtAST(expr)



    def parse_struct(self) -> StructAST:
        if self.next() != TokenKind.IDENTIFIER:
            raise Exception("문법 에러: 구조는 이름이 필요함")
        ident: str = self.current_value()
        self.next()
        self.expect(TokenKind.EUN, "문법 에러: 은/는 조사가 필요함")
        self.expect(TokenKind.NEXT, "문법 에러: \"다음\"이 필요함")
        var:list[str] = []
        while self.current() == TokenKind.VAR:
            var.append(self.parse_field())
        self.expect_seq(TokenKind.VALUE, TokenKind.EUL, TokenKind.HAVE,
                        TokenKind.DA, TokenKind.DOT, 
                        msg="문법 에러: 값을 가진다.로 끝나야함")

        return StructAST(ident, var)

    def parse_class(self):
        # 클래스는 영단어 class를 그대로 번역해서 쓰기 싫음
        # 또한 클래스를 유형으로 번역하는 것보다 더 좋은 대안이 없어서 
        # 일단은 유형이란 말이 안 맞지만 유형으로 바꿈 
        assert(self.check(TokenKind.TYPE))

        if self.current() != TokenKind.IDENTIFIER:
            raise Exception("문법 에러: 유형은 이름이 필요함")
        ident = self.current_value()
        self.next()
        self.expect(TokenKind.EUN, "문법 에러: 은/는 조사가 필요함")
        parent: str|None = None
        if self.current() == TokenKind.IDENTIFIER:
            parent = self.current_value()
            self.next()
            self.expect(TokenKind.UI, "문법 에러: 의 조사가 필요함")
            self.expect(TokenKind.CHILD, "문법 에러: 자식이고가 필요함")
            self.expect(TokenKind.GO, "문법 에러: 자식이고가 필요함")
        self.expect(TokenKind.NEXT, "문법 에러: 다음이 필요함")
        var_names: list[str] = []
        funcs: list[FuncAST] = []
        new_func: FuncAST|None = None
        while self.current() in [TokenKind.VAR, TokenKind.FUNC]:
            if self.current() == TokenKind.VAR:
                var_names.append(self.parse_field())
            else:
                func = self.parse_func()
                if func.ident == "초기화" and new_func == None:
                    new_func = func
                elif func.ident == "초기화":
                    raise Exception("문법 에러: 초기화 함수는 한 번만 정의 가능함")
                funcs.append(func)

        self.expect_seq(TokenKind.VALUE, TokenKind.EUL, TokenKind.HAVE,
                        TokenKind.DA, TokenKind.DOT, 
                        msg="문법 에러: 값을 가진다.로 끝나야함")
        return ClassAST(ident, var_names, funcs, parent, new_func)

    def parse_func(self) -> FuncAST:
        if self.next() != TokenKind.IDENTIFIER:
            raise Exception("문법 에러: 함수는 이름이 필요함")
        ident: str = self.current_value()
        self.next()
        if not self.check(TokenKind.HANDA):
            self.check(TokenKind.DA)
            
        self.expect(TokenKind.EUN, "문법 에러: 은/는 조사가 필요함")
        params: list[str] = []
        if self.current() == TokenKind.IDENTIFIER:
            while self.current() == TokenKind.IDENTIFIER:
                params.append(self.current_value())
                self.next()
                if self.current() == TokenKind.WA:
                    self.next()
                elif self.current() == TokenKind.RO:
                    self.next()
                    break
                else:
                    raise Exception("문법 에러: 와/과 또는 로 조사가 필요함")
            else:
                raise Exception("문법 에러: 매개변수 이름이 필요함")
        
        self.expect(TokenKind.NEXT, "문법 에러: 다음이 필요함")
        body: BodyAST = self.parse_body(TokenKind.PARAGRAPH)
        self.expect_seq(TokenKind.PARAGRAPH, TokenKind.EUL,
                        TokenKind.EXECUTE, TokenKind.HANDA,
                        TokenKind.DOT, msg="문법 에러: 문단을 실행한다.가 필요함")

        return FuncAST(ident, params, body)

    def parse_field(self) -> str:
        self.next()
        if self.current() != TokenKind.IDENTIFIER:
            raise Exception("문법 에러: 변수는 이름이 필요함")
        name: str = self.current_value()
        self.next()
        self.expect(TokenKind.KA, "문법 에러: 이/가 조사가 필요함")
        self.expect_seq(TokenKind.EXIST, TokenKind.DOT, 
                msg="문법 에러: \"있다.\"가 필요함")
        return name

    def parse_for(self, iter: ExprAST) -> ForAST:
        self.next()
        self.expect(TokenKind.ITNUN, "문법 에러: 있는이 필요함")
        self.expect(TokenKind.KAK, "문법 에러: 각이 필요함")
        self.expect(TokenKind.HANMOK, "문법 에러: 항목들을이 필요함")
        if self.current() != TokenKind.IDENTIFIER:
            raise Exception("문법 에러: 이름이 필요함")
        item = self.current_value()
        self.next()
        self.expect(TokenKind.RO, "문법 에러: 으로/로가 필요함")
        self.expect(TokenKind.GET, "문법 에러: 가져와가 필요함")
        self.expect(TokenKind.NEXT, "문법 에러: 다음이 필요함")

        tmp_loop = self.is_loop
        self.is_loop = True
        body = self.parse_body(TokenKind.PARAGRAPH)
        self.expect_seq(TokenKind.PARAGRAPH, TokenKind.EUL,
                        TokenKind.LOOP, TokenKind.HANDA,
                        TokenKind.DOT, msg="문법 에러: 문단을 반복한다.가 필요함")
        self.is_loop = tmp_loop
        return ForAST(iter, item, body)
        
    def parse_while(self) -> WhileAST:
        self.next()
        expr: ExprAST = self.parse_expr()
        if not self.check(TokenKind.RANUN) and not self.check(TokenKind.IN):
            raise Exception("문법 에러: 라는/인이 필요함")

        self.expect(TokenKind.DONGAN, "문법 에러: 동안이 필요함")
        self.expect(TokenKind.NEXT, "문법 에러: 다음이 필요함")
        tmp_loop = self.is_loop
        self.is_loop = True
        body = self.parse_body(TokenKind.PARAGRAPH)
        self.expect_seq(TokenKind.PARAGRAPH, TokenKind.EUL,
                        TokenKind.LOOP, TokenKind.HANDA,
                        TokenKind.DOT, msg="문법 에러: 문단을 반복한다.가 필요함")
        self.is_loop = tmp_loop
        return WhileAST(expr, body)

    def parse_if(self) -> CondAST:
        self.expect(TokenKind.IF, "문법 에러: 만약이 필요함")
        cond = self.parse_expr()
        self.expect(TokenKind.THEN, "문법 에러: 이면/면/라면/이라면이 필요함")
        self.expect(TokenKind.NEXT, "문법 에러: 다음이 필요함")
        then_body = self.parse_body(TokenKind.PARAGRAPH)
        
        self.expect_seq(TokenKind.PARAGRAPH, TokenKind.EUL,
                        TokenKind.EXECUTE, TokenKind.HANDA,
                        TokenKind.DOT, msg="문법 에러: 문단을 실행한다.가 필요함")
        
        if self.check(TokenKind.ELIF):
            else_cond = self.parse_if()
        elif self.check(TokenKind.ELSE):
            self.expect(TokenKind.NEXT, "문법 에러: 다음이 필요함")
            else_body = self.parse_body(TokenKind.PARAGRAPH)
            self.expect_seq(TokenKind.PARAGRAPH, TokenKind.EUL,
                            TokenKind.EXECUTE, TokenKind.HANDA,
                            TokenKind.DOT, msg="문법 에러: 문단을 실행한다.가 필요함")
            
            else_cond = CondAST(BoolAST(True), else_body, None)
        else:
            else_cond = None

        return CondAST(cond, then_body, else_cond)

    def parse_expr(self) -> ExprAST:
        return self.parse_or()


    def parse_or(self) -> ExprAST:
        left: ExprAST = self.parse_and()
        while self.check(TokenKind.OR):
            right: ExprAST = self.parse_and()
            left = BinAST(BinAST.OpKind.OP_OR, left, right)
        return left

    def parse_and(self) -> ExprAST:
        left: ExprAST = self.parse_equal()
        while self.check(TokenKind.AND) or \
            self.check(TokenKind.GO):
            right: ExprAST = self.parse_equal()
            left = BinAST(BinAST.OpKind.OP_AND, left, right)

        return left

    def parse_equal(self) -> ExprAST:
        left: ExprAST = self.parse_access()
        while self.current() == TokenKind.KA and \
                self.peek() != TokenKind.BECOME:
            self.next()
            right: ExprAST = self.parse_access()
            if self.check(TokenKind.RANG):
                op_kind: BinAST.OpKind
                if self.check(TokenKind.KAT):
                    if self.current() == TokenKind.DA and \
                        self.peek() == TokenKind.EUN:
                        self.next()
                        self.next()
                        self.expect(TokenKind.GEOT, "문법 에러: 것이 필요함")
                    elif self.current() == TokenKind.DA:
                        self.next()
                    else:
                        raise Exception("문법 에러: 같다/같다는 것이 필요함")
                    op_kind = BinAST.OpKind.OP_EQUAL
                elif self.check(TokenKind.NOTEQUAL):
                    if self.current() == TokenKind.DA and \
                        self.peek() == TokenKind.EUN:
                        self.next()
                        self.next()
                        self.expect(TokenKind.GEOT, "문법 에러: 것이 필요함")
                    elif self.current() == TokenKind.DA:
                        self.next()
                    else:
                        raise Exception("문법 에러: 다르다/다르다는 것이 필요함")
                    op_kind = BinAST.OpKind.OP_NOTEQUAL
                elif self.check(TokenKind.LIKE):

                    if self.current() == TokenKind.HAN and \
                        self.peek() == TokenKind.GEOT:
                        self.next()
                        self.next()
                    elif self.current(TokenKind.HANDA):
                        self.next()
                    else:
                        raise Exception("문법 에러: 비슷하다/비슷한 것이 필요함")
                    op_kind = BinAST.OpKind.OP_LIKE
                elif self.check(TokenKind.AN):
                    self.expect(TokenKind.LIKE, "문법 에러: 비슷하다/비슷한 것이 필요함")
                    if self.current() == TokenKind.HAN and \
                        self.peek() == TokenKind.GEOT:
                        self.next()
                        self.next()
                    elif self.current(TokenKind.HANDA):
                        self.next()
                    else:
                        raise Exception("문법 에러: 비슷하다/비슷한 것이 필요함")
                    op_kind = BinAST.OpKind.OP_NOTLIKE
                else:
                    raise Exception("문법 에러: 잘못된 단어가 있음")
                left = BinAST(op_kind, left, right)
            elif self.check(TokenKind.BODA):
                op_kind: BinAST.OpKind
                if self.check(TokenKind.GREATER):
                    if self.check(TokenKind.GEONA):
                        self.expect(TokenKind.KAT, "문법 에러: 같다 가 필요함")
                        op_kind = BinAST.OpKind.OP_GE
                    else:
                        op_kind = BinAST.OpKind.OP_GT
                elif self.check(TokenKind.LESS):
                    if self.check(TokenKind.GEONA):
                        self.expect(TokenKind.KAT, "문법 에러: 같다 가 필요함")
                        op_kind = BinAST.OpKind.OP_LE
                    else:
                        op_kind = BinAST.OpKind.OP_LT
                else:
                    raise Exception("문법 에러: 잘못된 단어가 있음")
                
                if self.current() == TokenKind.DA and \
                    self.peek() == TokenKind.EUN:
                    self.next()
                    self.next()
                    self.expect(TokenKind.GEOT, "문법 에러: 것이 필요함")
                elif self.current() == TokenKind.DA:
                    self.next()
                else:
                    raise Exception("문법 에러: 다/것 이 필요함")
                left = BinAST(op_kind, left, right)
            elif self.check(TokenKind.MANKEUM):
                op_kind: BinAST.OpKind
                if self.check(TokenKind.LEFT):
                    op_kind = BinAST.OpKind.OP_SHL
                elif self.check(TokenKind.RIGHT):
                    op_kind = BinAST.OpKind.OP_SHR
                self.expect(TokenKind.RO, "으로가 필요함")
                self.expect(TokenKind.GAN, "간이 필요함")
                if not self.check(TokenKind.GEOT) and not self.check(TokenKind.DA):
                    raise Exception("문법 에러: 다/것 이 필요함")
                left = BinAST(op_kind, left, right)

            else:
                raise Exception("문법 에러: 잘못된 단어가 있음")
        return left
    

    # todo: 생성 문법 만들기 문법은: 유형 나를 [다와 마로] 생성한다/생성한 것
    def parse_access(self, without_call = False) -> ExprAST:
        left = self.parse_primary()
        
        while self.current() == TokenKind.UI or \
            self.current() == TokenKind.ESEO or \
            self.current() == TokenKind.ANESEO or \
            (not without_call and self._is_call_check(self.current())):
            match self.current():
                case TokenKind.UI:
                    if self.next() != TokenKind.IDENTIFIER:
                        raise Exception("문법 에러: 이름이 필요함")
                    ident:str = self.current_value()
                    left = FieldAccessAST(left, ident)
                    self.next()
                case TokenKind.ESEO:
                    self.next()
                    idx: ExprAST = self.parse_expr()
                    self.expect(TokenKind.INDEX, "문법 에러: 번째가 필요함")
                    self.expect(TokenKind.ELEM, "문법 에러: 원소가 필요함")
                    left = IndexAccessAST(left, idx)
                case TokenKind.ANESEO:
                    self.next()
                    method: CallExprAST| CallStmtAST = self.parse_caller()
                    method.callee = MethodAccessAST(left, method.callee)
                    left = method
                case TokenKind.EUL:
                    call:ExprAST
                    if call := self.try_call_at_data(left):
                        left = call                       
                    else:
                        left = self.parse_caller(left)
                case TokenKind.WA|TokenKind.RO:
                    left = self.parse_caller(left)
                case TokenKind.HANDA|TokenKind.DA:
                    left = self.try_call_stmt(left)
                case TokenKind.GEOT|TokenKind.HAN:
                    left = self.try_call_expr(left)
        return left     
        
    def parse_caller(self, param = None) -> ExprAST:
        ro, eul = False, False
        call: ExprAST
        params: list[ExprAST] = []
        if param:
            params.append(param)
        else:
            callee_or_param: ExprAST = self.parse_access(True)
            
            if call := self.try_call_at_data(callee_or_param, []):
                return call
            elif call := self.try_call_expr(callee_or_param, []):
                return call
            elif call := self.try_call_stmt(callee_or_param, []):
                return call
            params.append(callee_or_param)

        while self.check(TokenKind.WA):
            params.append(self.parse_access(True))
        if self.check(TokenKind.RO):
            ro = True
        elif self.check(TokenKind.EUL):
            eul = True
        else:
            raise Exception("문법 에러: 로/으로/을/를이 필요함")

        callee_or_param = self.parse_access(True)
        if call := self.try_call_at_data(callee_or_param, params):
            if eul:
                raise Exception("문법 에러: 을/를은 한번만 쓸 수 있음")
            return call
        elif call := self.try_call_expr(callee_or_param, params):
            return call
        elif call := self.try_call_stmt(callee_or_param, params):
            return call
        params.append(callee_or_param)

        while self.check(TokenKind.WA):
            params.append(self.parse_access(True))
        if ro:
            self.expect(TokenKind.EUL, "문법 에러: 을/를이 필요함")
        elif eul:
            self.expect(TokenKind.RO, "문법 에러: 로/으로가 필요함")
        
        callee: ExprAST = self.parse_access(True)
        if call := self.try_call_expr(callee, params):
            return call
        elif call := self.try_call_stmt(callee, params):
            return call
        
        raise Exception("문법 에러: 잘못된 단어가 들어옴")
        
    def parse_primary(self) -> ExprAST:
        match self.current():
            case TokenKind.IDENTIFIER:
                value = self.current_value()
                self.next()
                return IdentifierAST(value)
            case TokenKind.NUMBER | TokenKind.HEX| \
                 TokenKind.OCT | TokenKind.BIN:
                value = self.current_value()
                self.next()
                return IntegerAST(value)
            case TokenKind.FLOAT:
                value = self.current_value()
                self.next()
                return FloatAST(value)
            case TokenKind.STRING:
                value = self.current_value()
                self.next()
                return StringAST(value)
            case TokenKind.TRUE:
                self.next()
                return BoolAST(True)
            case TokenKind.FALSE:
                self.next()
                return BoolAST(False)
            case TokenKind.NONE:
                self.next()
                return NoneAST()
            case TokenKind.LEFTPARENT:
                self.next()
                expr = self.parse_expr()
                self.expect(TokenKind.RIGHTPARENT, 
                            "문법 에러: )가 필요함")
                return expr
            case TokenKind.LEFTBRACE:
                if self.next() == TokenKind.RIGHTBRACE:
                    self.next()
                    return DictAST()
                
                dict_values: dict[ExprAST, ExprAST] = {}
                key: ExprAST = self.parse_expr()
                self.expect(TokenKind.EUN,
                            "문법 에러: 은/는 조사가 필요함.")
                
                value: ExprAST = self.parse_expr()
                dict_values[key] = value
                while self.check(TokenKind.ALSO):
                    key: ExprAST = self.parse_expr()
                    self.expect(TokenKind.EUN,
                                "문법 에러: 은/는 조사가 필요함.")
                    value: ExprAST = self.parse_expr()
                    dict_values[key] = value
                self.expect(TokenKind.RIGHTBRACE,
                            "문법 에러: }가 필요함")
                return DictAST(dict_values)
            case TokenKind.LEFTSQUARE:
                if self.next() == TokenKind.RIGHTSQUARE:
                    self.next()
                    return ArrayAST()
                elems: list[ExprAST] = []
                value: ExprAST = self.parse_expr()
                elems.append(value)
                while self.check(TokenKind.NEXT):
                    value = self.parse_expr()
                    elems.append(value)
                self.expect(TokenKind.RIGHTSQUARE,
                            "문법 에러: ]가 필요함")
                return ArrayAST(elems)
            case _:
                raise Exception("문법 에러: 잘못된 단어가 있음")

    def current(self) -> TokenKind:
        return self.lexer.current_token().kind

    def prev(self) -> TokenKind:
        return self.lexer.prev_token().kind

    def peek(self) -> TokenKind:
        return self.lexer.peek_token().kind

    def next(self) -> TokenKind:
        return self.lexer.advance_token().kind
    
    def current_value(self) -> str|int|float|bool|None:
        return self.lexer.current_token().get_value()

    def check(self, kind: TokenKind) -> bool:
        if self.current() == kind:
            self.next()
            return True
        return False

    def expect(self, kind: TokenKind, msg):
        if self.current() == kind:
            self.next()
            return
        raise Exception(msg)
    
    def expect_seq(self, *args, msg):
        for kind in args:
            self.expect(kind, msg)

    def _is_call_check(self, kind: TokenKind) -> bool:
        return kind == TokenKind.EUL or \
            kind == TokenKind.WA or \
            kind == TokenKind.RO or \
            kind == TokenKind.HANDA or \
            kind == TokenKind.DA or \
            kind == TokenKind.GEOT or \
            kind == TokenKind.HAN

    def try_call_at_data(self, callee: ExprAST, params: list[ExprAST] = []) \
        -> CallExprAST|CallStmtAST|None:
        if self.current() == TokenKind.EUL and self.peek() == TokenKind.CALL:
            self.next()
            self.next()
            if self.check(TokenKind.HANDA):
                return CallStmtAST(callee, params)
            elif self.check(TokenKind.HAN):
                self.expect(TokenKind.GEOT, "문법 에러: 것이 필요함")
                return CallExprAST(callee, params)
            else:
                raise Exception("문법 에러: 잘못된 단어가 들어옴")
        return None

    def try_call_expr(self, callee: ExprAST, 
                      params: list[ExprAST] = []) -> CallExprAST|None:
        if self.check(TokenKind.HAN):
            self.expect(TokenKind.GEOT, "문법 에러: 것이 필요함")
        elif not self.check(TokenKind.GEOT):
            return None
        return CallExprAST(callee, params)
    
    def try_call_stmt(self, callee: ExprAST, 
                      params: list[ExprAST] = []) -> CallStmtAST|None:
        if self.check(TokenKind.HANDA) or self.check(TokenKind.DA):
            return CallStmtAST(callee, params)
        return None
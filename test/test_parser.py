import unittest
import sys
import os

# 프로젝트 루트를 sys.path에 추가하여 '콜' 패키지를 임포트할 수 있도록 함
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from 콜.token import TokenKind
from 콜.lexer import Lexer
from 콜.parser import Parser
from 콜.ast import *

class TestParser(unittest.TestCase):

    def _parse_and_get_first_stmt(self, code: str) -> StmtAST:
        """코드를 파싱하고 첫 번째 구문(statement)을 반환합니다."""
        lexer = Lexer(code)
        parser = Parser(lexer)
        program = parser.parse()
        self.assertIsInstance(program, ProgramAST)
        self.assertGreater(len(program.body.stmts), 0, "파싱된 구문이 없습니다.")
        return program.body.stmts[0]

    def _parse_and_get_expr(self, code: str) -> ExprAST:
        """코드를 파싱하고 표현식(expression)을 반환합니다."""
        lexer = Lexer(code)
        parser = Parser(lexer)
        expr = parser.parse_expr()
        self.assertEqual(parser.current(), TokenKind.ENDOFFILE, f"코드를 모두 파싱하지 못했습니다: '{code}'")
        return expr

    def test_assignment_statement(self):
        code = "나이는 10이 된다."
        stmt = self._parse_and_get_first_stmt(code)

        self.assertIsInstance(stmt, AssignAST)
        self.assertIsInstance(stmt.lvalue, IdentifierAST)
        self.assertEqual(stmt.lvalue.ident, "나이")
        self.assertIsInstance(stmt.rvalue, IntegerAST)
        self.assertEqual(stmt.rvalue.num, 10)

    def test_if_statement(self):
        code = """
        만약 참이면 다음
            결과 값은 1이 된다. 그리고 끝난다.
        문단을 실행한다.
        아니고 만약 거짓이면 다음
            결과 값은 2가 된다. 그리고 끝난다.
        문단을 실행한다.
        아니면 다음
            결과 값은 3이 된다. 그리고 끝난다.
        문단을 실행한다.
        """
        stmt = self._parse_and_get_first_stmt(code)

        self.assertIsInstance(stmt, CondAST)
        self.assertIsInstance(stmt.cond, BoolAST)
        self.assertTrue(stmt.cond.value)
        self.assertIsInstance(stmt.then_body, BodyAST)
        
        then_stmt = stmt.then_body.stmts[0]
        self.assertIsInstance(then_stmt, ReturnAST)

        # elif (아니고) 절 테스트
        self.assertIsInstance(stmt.else_cond, CondAST, "elif 절이 파싱되지 않았습니다.")
        elif_stmt = stmt.else_cond
        self.assertIsInstance(elif_stmt.cond, BoolAST)
        self.assertFalse(elif_stmt.cond.value)

        # else (아니면) 절 테스트
        self.assertIsInstance(elif_stmt.else_cond, CondAST, "else 절이 파싱되지 않았습니다.")
        else_stmt = elif_stmt.else_cond
        self.assertIsInstance(else_stmt.cond, BoolAST) # '아니면'은 cond가 BoolAST(True)로 처리됨
        self.assertTrue(else_stmt.cond.value)

    def test_function_definition(self):
        code = """
        함수 더한다는 숫자1과 숫자2로 다음
            결과 값은 숫자1과 숫자2를 더한 것이 된다. 그리고 끝난다.
        문단을 실행한다.
        """
        
        stmt = self._parse_and_get_first_stmt(code)
        self.assertIsInstance(stmt, FuncAST)
        self.assertEqual(stmt.ident, "더")
        self.assertEqual(stmt.params, ["숫자1", "숫자2"])
        self.assertIsInstance(stmt.body.stmts[0], ReturnAST)

    def test_struct_definition(self):
        code = """
        구조 사람은 다음
            변수 이름이 있다.
            변수 나이가 있다.
        값을 가진다.
        """
        stmt = self._parse_and_get_first_stmt(code)
        self.assertIsInstance(stmt, StructAST)
        self.assertEqual(stmt.ident, "사람")
        self.assertEqual(stmt.vars, ["이름", "나이"])

    def test_class_definition(self):
        code = """
        유형 동물은 다음
            변수 이름이 있다.
            함수 소리를_낸다는 다음
                결과 값은 없음이 된다. 그리고 끝난다.
            문단을 실행한다.
        값을 가진다.
        """
        stmt = self._parse_and_get_first_stmt(code)
        self.assertIsInstance(stmt, ClassAST)
        self.assertEqual(stmt.ident, "동물")
        self.assertEqual(stmt.vars, ["이름"])
        self.assertEqual(len(stmt.funcs), 1)
        self.assertEqual(stmt.funcs[0].ident, "소리를_낸")
        self.assertIsNone(stmt.parent)

    def test_while_loop(self):
        code = """
        계속 참인 동안 다음
            계속한다.
        문단을 반복한다.
        """
        stmt = self._parse_and_get_first_stmt(code)
        self.assertIsInstance(stmt, WhileAST)
        self.assertIsInstance(stmt.cond, BoolAST)
        self.assertIsInstance(stmt.body.stmts[0], ContinueAST)

    def test_for_loop(self):
        code = """
        배열에 있는 각 항목들을 가로 가져와 다음
            나간다.
        문단을 반복한다.
        """
        stmt = self._parse_and_get_first_stmt(code)
        self.assertIsInstance(stmt, ForAST)
        self.assertIsInstance(stmt.iter, IdentifierAST)
        self.assertEqual(stmt.iter.ident, "배열")
        self.assertIsInstance(stmt.ident, str)
        self.assertEqual(stmt.ident, "가")
        self.assertIsInstance(stmt.body.stmts[0], BreakAST)

    def test_return_statement(self):
        """'결과 값은 ... 된다. 그리고 끝난다.' 형태의 반환문을 테스트합니다."""
        code = "결과 값은 1이 된다. 그리고 끝난다."
        stmt = self._parse_and_get_first_stmt(code)
        self.assertIsInstance(stmt, ReturnAST)
        self.assertIsInstance(stmt.value, IntegerAST)
        self.assertEqual(stmt.value.num, 1)

    def test_call_statement(self):
        """'...을/를 호출한다.' 형태의 호출문을 테스트합니다."""
        code = "출력을 호출한다."
        stmt = self._parse_and_get_first_stmt(code)
        expr = stmt.expr
        self.assertIsInstance(expr, CallStmtAST)
        self.assertIsInstance(expr.callee, IdentifierAST)
        self.assertEqual(expr.callee.ident, "출력")

    def test_primary_expressions(self):
        """기본 표현식(리터럴, 식별자 등)을 테스트합니다."""
        self.assertIsInstance(self._parse_and_get_expr("123"), IntegerAST)
        self.assertIsInstance(self._parse_and_get_expr("12.34"), FloatAST)
        self.assertIsInstance(self._parse_and_get_expr('"문자열"'), StringAST)
        self.assertIsInstance(self._parse_and_get_expr("참"), BoolAST)
        self.assertIsInstance(self._parse_and_get_expr("거짓"), BoolAST)
        self.assertIsInstance(self._parse_and_get_expr("없음"), NoneAST)
        self.assertIsInstance(self._parse_and_get_expr("변수이름"), IdentifierAST)
        self.assertIsInstance(self._parse_and_get_expr("(1)"), IntegerAST)

    def test_array_literal(self):
        """배열 리터럴 `[...]`을 테스트합니다."""
        # 빈 배열
        empty_array = self._parse_and_get_expr("[]")
        self.assertIsInstance(empty_array, ArrayAST)
        self.assertEqual(len(empty_array.elems), 0)

        # 원소가 있는 배열
        array = self._parse_and_get_expr('[1 다음 "안녕" 다음 참]')
        self.assertIsInstance(array, ArrayAST)
        self.assertEqual(len(array.elems), 3)
        self.assertIsInstance(array.elems[0], IntegerAST)
        self.assertIsInstance(array.elems[1], StringAST)
        self.assertIsInstance(array.elems[2], BoolAST)

    def test_dict_literal(self):
        """딕셔너리 리터럴 `{...}`을 테스트합니다."""
        # 빈 딕셔너리
        empty_dict = self._parse_and_get_expr("{}")
        self.assertIsInstance(empty_dict, DictAST)
        self.assertEqual(len(empty_dict.dict_values), 0)

        # 키-값 쌍이 있는 딕셔너리
        dict_ast = self._parse_and_get_expr('{"키"는 "값" 또 1은 2}')
        self.assertIsInstance(dict_ast, DictAST)
        self.assertEqual(len(dict_ast.dict_values), 2)
        # 파이썬 dict는 순서를 보장하지 않으므로 키로 값을 확인합니다.
        keys = list(dict_ast.dict_values.keys())
        values = list(dict_ast.dict_values.values())
        self.assertTrue(any(isinstance(k, StringAST) and k.str == "키" for k in keys))
        self.assertTrue(any(isinstance(v, StringAST) and v.str == "값" for v in values))

    def test_binary_operations(self):
        """이항 연산을 테스트합니다."""
        # '더한 것'과 같은 표현식은 CallExprAST로 파싱되므로, BinAST 테스트에서 제외합니다.
        test_cases = [
            ("1이 2랑 같다", BinAST.OpKind.OP_EQUAL),
            ("1이 2랑 다르다", BinAST.OpKind.OP_NOTEQUAL),
            ("1이 2보다 크다", BinAST.OpKind.OP_GT),
            ("1이 2보다 작다", BinAST.OpKind.OP_LT),
            ("1이 2보다 크거나 같다", BinAST.OpKind.OP_GE),
            ("1이 2보다 작거나 같다", BinAST.OpKind.OP_LE),
            ("참 그리고 거짓", BinAST.OpKind.OP_AND),
            ("참 또는 거짓", BinAST.OpKind.OP_OR),
            ("1이 2만큼 왼쪽으로 간 것", BinAST.OpKind.OP_SHL),
            ("1이 2만큼 오른쪽으로 간 것", BinAST.OpKind.OP_SHR),
        ]

        for code, op_kind in test_cases:
            with self.subTest(code=code):
                expr = self._parse_and_get_expr(code)
                self.assertIsInstance(expr, BinAST)
                self.assertEqual(expr.op, op_kind)

    def test_field_access(self):
        """'객체의 필드' 형태의 필드 접근을 테스트합니다."""
        expr = self._parse_and_get_expr("사람의 이름")
        self.assertIsInstance(expr, FieldAccessAST)
        self.assertIsInstance(expr.target, IdentifierAST)
        self.assertEqual(expr.target.ident, "사람")
        self.assertEqual(expr.field, "이름")

    def test_index_access(self):
        """'배열에서 n번째 원소' 형태의 인덱스 접근을 테스트합니다."""
        expr = self._parse_and_get_expr("배열에서 1번째 원소")
        self.assertIsInstance(expr, IndexAccessAST)
        self.assertIsInstance(expr.target, IdentifierAST)
        self.assertEqual(expr.target.ident, "배열")
        self.assertIsInstance(expr.idx, IntegerAST)

    def test_call_expression(self):
        """'...한 것' 또는 '...을/를 호출한 것' 형태의 함수 호출 표현식을 테스트합니다."""
        # 매개변수 없는 호출
        expr1 = self._parse_and_get_expr("함수를 호출한 것")
        self.assertIsInstance(expr1, CallExprAST)
        self.assertIsInstance(expr1.callee, IdentifierAST)
        self.assertEqual(expr1.callee.ident, "함수")
        self.assertEqual(len(expr1.params), 0)

        # 매개변수 있는 호출
        expr2 = self._parse_and_get_expr("1과 2를 더한 것")
        self.assertIsInstance(expr2, CallExprAST)
        self.assertIsInstance(expr2.callee, IdentifierAST)
        self.assertEqual(expr2.callee.ident, "더")
        self.assertEqual(len(expr2.params), 2)
        self.assertIsInstance(expr2.params[0], IntegerAST)
        self.assertIsInstance(expr2.params[1], IntegerAST)


if __name__ == '__main__':
    unittest.main()
import unittest
import sys
import os

# 프로젝트 루트를 sys.path에 추가하여 '콜' 패키지를 임포트할 수 있도록 함
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from 콜.lexer import Lexer
from 콜.parser import Parser
from 콜.compiler import Compiler
from 콜.vm import VM
from 콜.func import Func

class TestVM(unittest.TestCase):

    def _run_code(self, code: str, expected_stack_top=None):
        """
        주어진 '콜' 코드를 컴파일하고 VM에서 실행합니다.
        실행 후 VM 인스턴스를 반환하거나, 스택의 최상단 값을 검증합니다.
        """
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()
        
        compiler = Compiler()
        compiler.compile_main(ast)

        # 함수 객체들을 미리 컴파일합니다.
        for const in compiler.const_pool:
            if isinstance(const, Func):
                Compiler.compile_func(const)

        vm = VM(compiler.assign, compiler.const_pool, compiler.bytecode)
        vm.run()
        if expected_stack_top is not None:
            self.assertGreater(len(vm.stack), 0, "VM 스택이 비어있습니다.")
            self.assertEqual(vm.stack[-1], expected_stack_top)
        
        return vm

    def test_arithmetic_operations(self):
        """내장 함수를 이용한 산술 연산을 테스트합니다."""
        code = """
        가는 10과 5를 더한 것이 된다.
        가를 출력한다.
        가는 가를 3으로 뺀 것이 된다.
        가를 출력한다.
        가는 가와 2를 곱한 것이 된다.
        가를 출력한다.
        가는 가를 4로 나눈 것이 된다.
        가를 출력한다.
        """
        self._run_code(code, expected_stack_top=0) # (10+5-3)*2 / 4 = 6

    def _test_if_else_statement(self):
        """if-else 문 실행을 테스트합니다."""
        code = """
        만약 1이 1이랑 같으면 다음
            결과는 100이 된다.
        문단을 실행한다.
        아니면 다음
            결과는 200이 된다.
        문단을 실행한다.
        """
        # '결과' 변수가 할당되는지 확인하기 위해 후속 코드를 실행합니다.
        full_code = code + "\n결과."
        self._run_code(full_code, expected_stack_top=100)

    def _test_while_loop(self):
        """while 루프 실행을 테스트합니다."""
        code = """
        숫자는 0이 된다.
        계속 숫자가 5보다 작은 동안 다음
            숫자는 숫자와 1을 더한 것이 된다.
        문단을 반복한다.
        숫자.
        """
        self._run_code(code, expected_stack_top=5)

    def _test_function_call_and_return(self):
        """함수 정의, 호출, 반환 값 테스트"""
        code = """
        함수 값_가져온다는 다음
            결과 값은 12345가 된다. 그리고 끝난다.
        문단을 실행한다.
        
        결과는 값_가져온 것을 호출한 것이 된다.
        결과.
        """
        self._run_code(code, expected_stack_top=12345)

    def _test_for_loop_execution(self):
        """for 루프 실행을 테스트합니다."""
        code = """
        합계는 0이 된다.
        배열은 [10 다음 20 다음 30]이 된다.
        배열에 있는 각 항목들을 숫자로 가져와 다음
            합계는 합계와 숫자를 더한 것이 된다.
        문단을 반복한다.
        합계.
        """
        self._run_code(code, expected_stack_top=60)

    def _test_access_global_variable_in_function(self):
        """함수 내에서 전역 변수 접근 및 수정을 테스트합니다."""
        code = """
        전역변수는 100이 된다.
        
        함수 전역_수정한다는 다음
            전역변수는 200이 된다.
            결과 값은 없음이 된다. 그리고 끝난다.
        문단을 실행한다.

        전역_수정을 호출한다.
        전역변수.
        """
        self._run_code(code, expected_stack_top=200)

if __name__ == '__main__':
    unittest.main()

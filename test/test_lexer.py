import unittest
import sys
import os

# 프로젝트 루트를 sys.path에 추가하여 '콜' 패키지를 임포트할 수 있도록 함
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from 콜.lexer import Lexer
from 콜.token import Token, TokenKind

class TestLexer(unittest.TestCase):

    def _assert_tokens(self, code: str, expected_tokens: list[Token]):
        lexer = Lexer(code)
        for expected_token in expected_tokens:
            token = lexer.current_token()
            self.assertEqual(token.kind, expected_token.kind, f"코드: '{code}'")
            if expected_token.str:
                self.assertEqual(token.str, expected_token.str, f"코드: '{code}'")
            lexer.advance_token()
        
        # 마지막 토큰이 ENDOFFILE인지 확인
        self.assertEqual(lexer.current_token().kind, TokenKind.ENDOFFILE, f"코드: '{code}'")

    def test_numbers(self):
        self._assert_tokens("123", [Token(TokenKind.NUMBER, "123")])
        self._assert_tokens("12.34", [Token(TokenKind.FLOAT, "12.34")])
        self._assert_tokens("-5", [Token(TokenKind.NUMBER, "-5")])

    def test_string(self):
        self._assert_tokens('"안녕 세상"', [Token(TokenKind.STRING, "안녕 세상")])
        self._assert_tokens("'작은따옴표'", [Token(TokenKind.STRING, "작은따옴표")])

    def test_identifier_and_keywords(self):
        self._assert_tokens("변수이름", [Token(TokenKind.IDENTIFIER, "변수이름")])
        self._assert_tokens("만약 참이면", [
            Token(TokenKind.IF),
            Token(TokenKind.TRUE),
            Token(TokenKind.THEN)
        ])

    def test_simple_assignment(self):
        code = "나이는 10이다."
        expected = [
            Token(TokenKind.IDENTIFIER, "나이"),
            Token(TokenKind.EUN),
            Token(TokenKind.NUMBER, "10"),
            Token(TokenKind.DA),
            Token(TokenKind.DOT)
        ]
        self._assert_tokens(code, expected)

    def test_line_comment(self):
        code = "주석 이것은 주석입니다.\n나이는 10이다."
        expected = [
            Token(TokenKind.IDENTIFIER, "나이"),
            Token(TokenKind.EUN),
            Token(TokenKind.NUMBER, "10"),
            Token(TokenKind.DA),
            Token(TokenKind.DOT)
        ]
        self._assert_tokens(code, expected)

    def test_block_comment(self):
        code = "주석 시작\n이것은\n여러 줄\n주석입니다.\n주석 끝\n결과는 5이다."
        expected = [
            Token(TokenKind.IDENTIFIER, "결과"),
            Token(TokenKind.EUN),
            Token(TokenKind.NUMBER, "5"),
            Token(TokenKind.DA),
            Token(TokenKind.DOT)
        ]
        self._assert_tokens(code, expected)

    def test_all_tokens(self):
        # 각 토큰 종류에 대한 간단한 테스트 케이스
        token_test_cases = {
            # PUNCTUATION
            "(": [Token(TokenKind.LEFTPARENT)],
            ")": [Token(TokenKind.RIGHTPARENT)],
            "[": [Token(TokenKind.LEFTSQUARE)],
            "]": [Token(TokenKind.RIGHTSQUARE)],
            "{": [Token(TokenKind.LEFTBRACE)],
            "}": [Token(TokenKind.RIGHTBRACE)],
            # LITERALS
            "0x1A": [Token(TokenKind.HEX, "0x1A")],
            "0o71": [Token(TokenKind.OCT, "0o71")],
            "0b101": [Token(TokenKind.BIN, "0b101")],
            # POST
            "은 는 을 를 와 과 의 로 으로 한 하는 이 가 고 이고 그리고 또는 이거나 이면 면 이라면 라면 라는 동안 계속 있는 에서 에 각 인 안에서 구조 유형 다음 변수 함수 만큼 옮긴 안 거나 보다 만약 결과 없이 아니고 아니면 번째 .": [
                Token(TokenKind.EUN), Token(TokenKind.EUN), Token(TokenKind.EUL), Token(TokenKind.EUL), Token(TokenKind.WA), Token(TokenKind.WA), Token(TokenKind.UI), Token(TokenKind.RO), Token(TokenKind.RO), Token(TokenKind.HAN), Token(TokenKind.HAN), Token(TokenKind.KA), Token(TokenKind.KA), Token(TokenKind.GO), Token(TokenKind.GO), Token(TokenKind.AND), Token(TokenKind.OR), Token(TokenKind.OR), Token(TokenKind.THEN), Token(TokenKind.THEN), Token(TokenKind.THEN), Token(TokenKind.THEN), Token(TokenKind.RANUN), Token(TokenKind.DONGAN), Token(TokenKind.CONT), Token(TokenKind.ITNUN), Token(TokenKind.ESEO), Token(TokenKind.E), Token(TokenKind.KAK), Token(TokenKind.IN), Token(TokenKind.ANESEO), Token(TokenKind.STRUCT), Token(TokenKind.TYPE), Token(TokenKind.NEXT), Token(TokenKind.VAR), Token(TokenKind.FUNC), Token(TokenKind.MANKEUM), Token(TokenKind.ONGIN), Token(TokenKind.AN), Token(TokenKind.GEONA), Token(TokenKind.BODA), Token(TokenKind.IF), Token(TokenKind.RESULT), Token(TokenKind.UPSI), Token(TokenKind.ELIF), Token(TokenKind.ELSE), Token(TokenKind.INDEX), Token(TokenKind.DOT)
            ],
            # MIDDLE
            "문단 다 이다 있다 값 한다 하다 자식 왼쪽 오른쪽 것 원소": [
                Token(TokenKind.PARAGRAPH), Token(TokenKind.DA), Token(TokenKind.DA), Token(TokenKind.EXIST), Token(TokenKind.VALUE), Token(TokenKind.HANDA), Token(TokenKind.HANDA), Token(TokenKind.CHILD), Token(TokenKind.LEFT), Token(TokenKind.RIGHT), Token(TokenKind.GEOT), Token(TokenKind.ELEM)
            ],
            # REMAIN
            "반복 끝낸 참 거짓 없음 생성 실행 가진 같 비슷 다르 크 작 호출": [
                Token(TokenKind.LOOP), Token(TokenKind.FINISH), Token(TokenKind.TRUE), Token(TokenKind.FALSE), Token(TokenKind.NONE), Token(TokenKind.NEW), Token(TokenKind.EXECUTE), Token(TokenKind.HAVE), Token(TokenKind.KAT), Token(TokenKind.LIKE), Token(TokenKind.NOTEQUAL), Token(TokenKind.GREATER), Token(TokenKind.LESS), Token(TokenKind.CALL)
            ]
        }

        for code, expected in token_test_cases.items():
            with self.subTest(code=code):
                self._assert_tokens(code, expected)

    def test_combined_tokens(self):
            # 식별자와 조사가 합쳐진 경우
            self._assert_tokens("가는", [
                Token(TokenKind.IDENTIFIER, "가"),
                Token(TokenKind.EUN)
            ])
            self._assert_tokens("결과를", [
                Token(TokenKind.IDENTIFIER, "결과"),
                Token(TokenKind.EUL)
            ])
            # 키워드와 다른 토큰이 합쳐진 경우
            self._assert_tokens("반복한다.", [
                Token(TokenKind.LOOP),
                Token(TokenKind.HANDA),
                Token(TokenKind.DOT)
            ])
            # 괄호와 바로 붙어있는 경우
            self._assert_tokens("1과 가를 더한다.", [
                Token(TokenKind.NUMBER, "1"),
                Token(TokenKind.WA),
                Token(TokenKind.IDENTIFIER, "가"),
                Token(TokenKind.EUL),
                Token(TokenKind.IDENTIFIER, "더"),
                Token(TokenKind.HANDA),
                Token(TokenKind.DOT)
            ])

if __name__ == '__main__':
    # `python tests/test_lexer.py`로 실행
    unittest.main()
from enum import Enum, auto
from .none import NoneObject

class TokenKind(Enum):
    UNDEFINED = auto()

    # WITH NON HANGUL
    LEFTPARENT = auto() # (
    RIGHTPARENT = auto() # )
    LEFTSQUARE = auto() # [
    RIGHTSQUARE = auto() # ]
    LEFTBRACE = auto() # {
    RIGHTBRACE = auto() # }
    NUMBER = auto() # 1, 2, 3, -12
    FLOAT = auto() # 2.12
    HEX = auto() # 0x123
    OCT = auto() # 0o123
    BIN = auto() # 0b0101
    STRING = auto() # "가나다"/'가나'



    # POST TOKEN
    EUN = auto() # 은/는
    EUL = auto() # 을/를
    WA = auto() # 와/과
    UI = auto() # 의
    RO = auto() # 로/으로
    HAN = auto() # 하는 / 한
    KA = auto() # 이/가
    GO = auto() # 고/이고
    AND = auto() # 그리고
    OR = auto() # 또는/이거나
    THEN = auto() # 이면/면/라면/이라면
    RANUN = auto() # 라는
    DONGAN = auto() # 동안
    ITNUN = auto() # 있는
    ESEO = auto() # 에서
    E = auto() # 에
    KAK = auto() # 각
    IN = auto() # 인
    ANESEO = auto() # 안에서
    STRUCT = auto() # 구조
    TYPE = auto() # 유형
    NEXT = auto() # 다음
    VAR = auto() # 변수
    FUNC = auto() # 함수
    MANKEUM = auto() # 만큼
    ONGIN = auto() # 옮긴
    AN = auto() # 안
    GEONA = auto() # 거나
    BODA = auto() # 보다
    IF = auto() # 만약
    RESULT = auto() # 결과
    UPSI = auto() # 없이
    ELIF = auto() # 아니고
    ELSE = auto() # 아니면
    INDEX = auto() # 번째
    GET = auto() # 대해
    ALSO = auto() # 또
    RANG = auto() # 랑/이랑
    GAN = auto() # 간
    HANMOK = auto() # 항목들을
    DOT = auto() # .

    # MIDDLE TOKEN
    PARAGRAPH = auto() # 문단
    DA = auto() # 다/이다
    HANDA = auto() # 한다/ 하다
    EXIST = auto() # 있다
    VALUE = auto() # 값
    CHILD = auto() # 자식
    LEFT = auto() # 왼쪽
    RIGHT = auto() # 오른쪽
    GEOT = auto() # 것
    ELEM = auto() # 원소

    # REMAIN TOKEN
    LOOP = auto() # 반복
    CONT = auto() # 계속
    BREK = auto() # 나간
    FINISH = auto() # 끝낸
    TRUE = auto() # 참
    FALSE = auto() # 거짓
    NONE = auto() # 없음
    NEW = auto() # 생성
    EXECUTE = auto() # 실행
    HAVE = auto() # 가진
    KAT = auto() # 같
    LIKE = auto() # 비슷
    NOTEQUAL = auto() # 다르
    GREATER = auto() # 크
    LESS = auto() # 작
    CALL = auto() # 호출
    BECOME = auto() # 된
    IDENTIFIER = auto() # 가, 나, 다

    # etc
    COMMENT = auto() # 주석 ㅁㄴㅇㄹ/ 주석 시작 ~ 끝
    ENDOFFILE = auto() # 파일 끝

class Token:
    PUNCTUATION = {
        "(":TokenKind.LEFTPARENT,
        ")":TokenKind.RIGHTPARENT,
        "{":TokenKind.LEFTBRACE,
        "}":TokenKind.RIGHTBRACE,
        "[":TokenKind.LEFTSQUARE,
        "]":TokenKind.RIGHTSQUARE
    }

    POST = {
        "은": TokenKind.EUN, "는": TokenKind.EUN,
        "을": TokenKind.EUL, "를": TokenKind.EUL,
        "와": TokenKind.WA, "과": TokenKind.WA,
        "의": TokenKind.UI,
        "으로": TokenKind.RO, "로": TokenKind.RO, 
        "한": TokenKind.HAN, "하는": TokenKind.HAN,
        "이": TokenKind.KA, "가": TokenKind.KA,
        "고": TokenKind.GO, "이고": TokenKind.GO,
        "그리고": TokenKind.AND,
        "또는": TokenKind.OR, "이거나": TokenKind.OR,
        "이면": TokenKind.THEN, "면": TokenKind.THEN,
        "이라면": TokenKind.THEN, "라면": TokenKind.THEN,
        "라는": TokenKind.RANUN,
        "동안": TokenKind.DONGAN,
        "있는": TokenKind.ITNUN,
        "에서": TokenKind.ESEO,
        "에": TokenKind.E,
        "각": TokenKind.KAK,
        "인": TokenKind.IN,
        "안에서": TokenKind.ANESEO,
        "구조": TokenKind.STRUCT,
        "유형": TokenKind.TYPE,
        "다음": TokenKind.NEXT,
        "변수": TokenKind.VAR,
        "함수": TokenKind.FUNC,
        "만큼": TokenKind.MANKEUM,
        "간": TokenKind.GAN,
        "안": TokenKind.AN,
        "거나": TokenKind.GEONA,
        "보다": TokenKind.BODA,
        "만약": TokenKind.IF,
        "결과": TokenKind.RESULT,
        "없이": TokenKind.UPSI,
        "아니고": TokenKind.ELIF,
        "아니면": TokenKind.ELSE,
        "번째": TokenKind.INDEX,
        "가져와": TokenKind.GET,
        "또": TokenKind.ALSO,
        "랑": TokenKind.RANG,
        "이랑": TokenKind.RANG,
        "항목들을": TokenKind.HANMOK,
        ".": TokenKind.DOT
    }

    POST_SORT_KEY = tuple(sorted(POST, key=len, reverse=True))

    MIDDLE = {
        "문단": TokenKind.PARAGRAPH,
        "다": TokenKind.DA, "이다": TokenKind.DA,
        "있다": TokenKind.EXIST,
        "값": TokenKind.VALUE,
        "한다": TokenKind.HANDA, "하다": TokenKind.HANDA,
        "자식": TokenKind.CHILD,
        "왼쪽": TokenKind.LEFT,
        "오른쪽": TokenKind.RIGHT,
        "것": TokenKind.GEOT,
        "원소": TokenKind.ELEM,
    }

    MIDDLE_SORT_KEY = tuple(sorted(MIDDLE, key=len, reverse=True))

    REMAIN = {
        "반복": TokenKind.LOOP,
        "나간": TokenKind.BREK,
        "계속": TokenKind.CONT,
        "끝난": TokenKind.FINISH,
        "참": TokenKind.TRUE,
        "거짓": TokenKind.FALSE,
        "없음": TokenKind.NONE,
        "생성": TokenKind.NEW,
        "실행": TokenKind.EXECUTE,
        "가진": TokenKind.HAVE,
        "같": TokenKind.KAT,
        "비슷": TokenKind.LIKE,
        "다르": TokenKind.NOTEQUAL,
        "크": TokenKind.GREATER,
        "작": TokenKind.LESS,
        "호출": TokenKind.CALL,
        "된": TokenKind.BECOME
    }

    def __init__(self, kind: TokenKind = TokenKind.UNDEFINED, str: str = ""):
        if type(kind) != TokenKind:
            raise Exception("asdfsadf")
        self.kind: TokenKind = kind
        self.str = str

    def set_str(self, str: str):
        self.str = str

    def get_value(self) -> str|int|float|bool|NoneObject|None:
        match self.kind:
            case TokenKind.STRING:
                return self.str
            case TokenKind.NUMBER:
                return int(self.str)
            case TokenKind.HEX:
                return int(self.str, 16)
            case TokenKind.OCT:
                return int(self.str, 8)
            case TokenKind.BIN:
                return int(self.str, 2)
            case TokenKind.IDENTIFIER:
                return self.str
            case TokenKind.FLOAT:
                return float(self.str)
            case TokenKind.TRUE:
                return True
            case TokenKind.FALSE:
                return False
            case TokenKind.NONE:
                return NoneObject()
            case _:
                return None

    def __bool__(self):
        return self.kind != TokenKind.UNDEFINED

    def __repr__(self) -> str:
        if self.str:
            return f"Token({self.kind.name}, '{self.str}')"
        return f"Token({self.kind.name})"
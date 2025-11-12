from .token import Token, TokenKind



class Lexer:
    def __init__(self, src: str):
        self.src: str = src
        self.pos: int = 0
        self.prev: Token = Token()
        self.cur: Token = Token()
        self.next: Token = Token()
        self.advance_token()

    def _is_out_of_bound_src(self, idx: int) -> bool:
        return len(self.src) <= idx

    def _skip_comment(self):
        assert(self.src[self.pos:self.pos+2] == "주석")
        self.pos += 2
        while self.src[self.pos] in ' \t':
            self.pos += 1
        if self.src[self.pos:self.pos+2] == "시작":
            while self.src[self.pos:self.pos+4] != "주석 끝":
                self.pos += 1
                if self._is_out_of_bound_src(self.pos):
                    raise Exception("Token Error: Comment")
            self.pos += 4
        else:
            while not self._is_out_of_bound_src(self.pos) and \
                self.src[self.pos] not in '\n\r':
                self.pos += 1
            self.pos += 1
        while not self._is_out_of_bound_src(self.pos) and \
                self.src[self.pos].isspace():
            self.pos += 1

    
    def _scan_punctuation(self) -> bool:
        token: Token = Token(
            Token.PUNCTUATION.get(self.src[self.pos], TokenKind.UNDEFINED))
        if token:
            self.next = token
            self.pos += 1
            return True
        return False

    def _scan_literal(self) -> bool:
        if self.src[self.pos] in "\"'":
            end_char = self.src[self.pos]
            self.pos += 1
            end_pos = self.pos
            while self.src[end_pos] != end_char or \
                self.src[end_pos-1] == "\\":
                if not self.src[end_pos].isprintable() and \
                    self.src[end_pos] == '\n':
                    raise Exception("Token Error: string")
                end_pos += 1
            self.next = Token(TokenKind.STRING)
            self.next.set_str(self.src[self.pos:end_pos])
            self.pos = end_pos + 1
            return True
        else:
            end_pos = self.pos
            if self.src[self.pos] in "+-":
                end_pos += 1
                if self._is_out_of_bound_src(end_pos):
                    raise Exception("Token Error: Number")
            if not self.src[end_pos].isdigit():
                return False
            
            if self.src[end_pos:end_pos+2] in ["0x","0X"]:
                end_pos += 2
                if self.src[end_pos] not in "0123456789ABCDEFabcdef":
                    raise Exception("Token Error: Hex Number")
                while not self._is_out_of_bound_src(end_pos) and \
                        self.src[end_pos] in "0123456789ABCDEFabcdef":
                    end_pos += 1
                self.next = Token(TokenKind.HEX)
                self.next.set_str(self.src[self.pos: end_pos])
                self.pos = end_pos
                return True
            elif self.src[end_pos:end_pos+2] in ["0o","0O"]:
                end_pos += 2
                if self.src[end_pos] not in "01234567":
                    raise Exception("Token Error: Oct Number")
                while not self._is_out_of_bound_src(end_pos) and \
                        self.src[end_pos] in "01234567":
                    end_pos += 1
                self.next = Token(TokenKind.OCT)
                self.next.set_str(self.src[self.pos: end_pos])
                self.pos = end_pos
                return True
            elif self.src[end_pos:end_pos+2] in ["0b", "0B"]:
                end_pos += 2
                if self.src[end_pos] not in "01":
                    raise Exception("Token Error: Bin Number")
                while not self._is_out_of_bound_src(end_pos) and \
                        self.src[end_pos] in "01":
                    end_pos += 1
                self.next = Token(TokenKind.BIN)
                self.next.set_str(self.src[self.pos: end_pos])
                self.pos = end_pos
                return True
            

            while not self._is_out_of_bound_src(end_pos) and \
                    self.src[end_pos].isdigit():
                end_pos += 1
            if not self._is_out_of_bound_src(end_pos) and \
                self.src[end_pos] == ".":
                end_pos += 1
            else:
                self.next = Token(TokenKind.NUMBER)
                self.next.set_str(self.src[self.pos: end_pos])
                self.pos = end_pos
                return True
            while not self._is_out_of_bound_src(end_pos) and \
                    self.src[end_pos].isdigit():
                end_pos += 1

            self.next = Token(TokenKind.FLOAT)
            self.next.set_str(self.src[self.pos: end_pos])
            self.pos = end_pos
            return True

    def _scan_post(self, word: str) -> bool:
        token: Token = Token(Token.POST.get(word, TokenKind.UNDEFINED))
        if token:
            self.next = token
            self.pos += len(word)
            return True
        return False

    def _get_without_post(self, word: str) -> str:
        for k in Token.POST_SORT_KEY:
            if word.endswith(k):
                return word[:-len(k)]
        return word

    def _scan_middle(self, word: str) -> bool:
        token: Token = Token(Token.MIDDLE.get(word, TokenKind.UNDEFINED))
        if token:
            self.next = token
            self.pos += len(word)
            return True
        return False

    def _get_without_middle(self, word: str) -> str:
        for k in Token.MIDDLE_SORT_KEY:
            if word.endswith(k):
                return word[:-len(k)]
        return word
    
    def _scan_remain(self, word: str) -> bool:
        token: Token = Token(Token.REMAIN.get(word, TokenKind.UNDEFINED))
        if token:
            self.next = token
            self.pos += len(word)
            return True
        return False

    def _scan(self):
        while not self._is_out_of_bound_src(self.pos) and \
                 self.src[self.pos].isspace():
                self.pos += 1
        
        if self._is_out_of_bound_src(self.pos):
            self.next = Token(TokenKind.ENDOFFILE)
            return

        try:
            if self.src[self.pos:self.pos+2] == "주석":
                self._skip_comment()
                self._scan()
                return

            word: str = self.src[self.pos:].split(maxsplit=1)[0]
            if self._scan_punctuation():
                return
            elif self._scan_literal():
                return
            if word[-1] == ']' or word[-1] == ")" or word[-1] == "}":
                word = word[:-1]
            if self._scan_post(word):
                return
            
            word = self._get_without_post(word)

            if word[-1] == ']' or word[-1] == ")" or word[-1] == "}":
                word = word[:-1]
                
            if self._scan_middle(word):
                return
            word = self._get_without_middle(word)

            if word[-1] == ']' or word[-1] == ")" or word[-1] == "}":
                word = word[:-1]

            if self._scan_remain(word):
                return

            for ch in word:
                if not ('가' <= ch <= '힣' or '0' <= ch <= '9' or ch == '_'):
                    raise Exception("Token Error: Identifier")
            self.next = Token(TokenKind.IDENTIFIER)
            self.next.set_str(word)
            self.pos += len(word)

        except Exception as e:
            self.next = Token(TokenKind.UNDEFINED)
            raise e

    def prev_token(self):
        return self.prev

    def peek_token(self) -> Token:
        if not self.next:
            self._scan()
        return self.next

    def advance_token(self) -> Token:
        if not self.next:
            self._scan()
        self.prev = self.cur
        self.cur = self.next
        self.next = Token()
        return self.cur
    
    def current_token(self) -> Token:
        return self.cur
    
    def print(self):
        i = 0
        while self.current_token().kind != TokenKind.ENDOFFILE and \
            self.current_token().kind != TokenKind.UNDEFINED:
            print(f"토큰[{i}]: {self.current_token()}")
            self.advance_token()
            i += 1
        print(f"토큰[{i}]: {self.current_token()}")
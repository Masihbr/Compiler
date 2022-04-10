import enum
from collections import defaultdict

from file_handler import FileHandler


class TokenType(enum.Enum):
    NUMBER = "NUMBER"
    ID = "ID"
    KEYWORD = "KEYWORD"
    SYMBOL = "SYMBOL"
    COMMENT = "COMMENT"
    WHITESPACE = "WHITESPACE"


class LexicalError(enum.Enum):
    INVALID_INPUT = 'Invalid input'
    UNCLOSED_COMMENT = 'Unclosed comment'
    UNMATCHED_COMMENT = 'Unmatched comment'
    INVALID_NUMBER = 'Invalid number'


WHITESPACES = [' ', '\n', '\r', '\t', '\v', '\f']
SINGLE_SYMBOLS = [';', ':', ',', '[', ']', '(', ')', '+', '-', '<']
KEYWORDS = ("break", "continue", "def", "else", "if", "return", "while")


class Scanner:
    input_filename = 'input.txt'

    def __init__(self):
        self.file_handler = FileHandler()
        self.code = self.file_handler.read_all()
        if self.code[-1] != '\n':
            self.code += '\n'

        self.lineno = 1
        self.start_cursor = 0
        self.end_cursor = 0

        self.state = 0

        self.tokens = defaultdict(list)
        self.errors = defaultdict(list)
        self.symbols = list(KEYWORDS)

    def get_next_token(self):
        while self.end_cursor < len(self.code):
            char = self.code[self.end_cursor]
            self.end_cursor += 1  # now char is self.code[self.end_cursor - 1]

            error = self.set_next_state(char)
            if error:
                self.log_error(error)
                self.start_cursor = self.end_cursor
                self.state = 0

            token_type = self.check_final_states()
            if token_type:
                token = self.code[self.start_cursor:self.end_cursor]
                if token_type not in [TokenType.WHITESPACE, TokenType.COMMENT]:
                    self.tokens[self.lineno].append((token_type.value, token))
                self.start_cursor = self.end_cursor
                self.state = 0
                return token_type, token

        if self.state == 8:
            self.log_error(LexicalError.UNCLOSED_COMMENT)
        """
        print(self.general_to_string(self.errors))
        print(self.general_to_string(self.tokens))
        print(self.symbols_to_string(self.symbols))
        """
        self.file_handler.write(address="tokens",
                                string=self.general_to_string(self.tokens))
        self.file_handler.write(address="lexical_errors",
                                string=self.general_to_string(self.errors))
        self.file_handler.write(address="symbol_table",
                                string=self.symbols_to_string(self.symbols))

    def set_next_state(self, char):
        # Initial state
        if self.state == 0:
            if char.isdigit():
                self.state = 1  # Number
            elif char.isalpha():
                self.state = 5  # Letter (ID, Keyword)
            elif char == '/':
                self.state = 7  # /* comment */
            elif char == '#':
                self.state = 11  # comment
            elif char in WHITESPACES:
                self.lineno += int(char == '\n')
                self.state = 13
            elif char in SINGLE_SYMBOLS:
                self.state = 14
            elif char == '*':
                self.state = 15
            elif char == '=':
                self.state = 18
            else:
                return LexicalError.INVALID_INPUT
        # Number no dot state
        elif self.state == 1:
            if char.isdigit():
                self.state = 1
            elif char == '.':
                self.state = 2
            elif char in WHITESPACES or char in SINGLE_SYMBOLS or char in ['*', '=', '/', '#']:
                self.state = 4
            else:
                return LexicalError.INVALID_NUMBER
        # Number with dot initial state
        elif self.state == 2:
            if char.isdigit():
                self.state = 3  # should visit digit after dot
            else:
                return LexicalError.INVALID_NUMBER
        # Number with dot state
        elif self.state == 3:
            if char.isdigit():
                self.state = 3
            elif char in WHITESPACES or char in SINGLE_SYMBOLS or char in ['*', '=', '/', '#']:
                self.state = 4
            else:
                return LexicalError.INVALID_NUMBER
        # ID, Keyword state
        elif self.state == 5:
            if char.isalnum():
                self.state = 5
            elif char in WHITESPACES or char in SINGLE_SYMBOLS or char in ['*', '=', '/', '#']:
                self.state = 6
            else:
                return LexicalError.INVALID_INPUT
        # /* comment */ state
        elif self.state == 7:
            if char == '*':
                self.state = 8
            else:
                self.end_cursor -= 1
                return LexicalError.INVALID_INPUT
        # /* comment */ state
        elif self.state == 8:
            if char == '*':
                self.state = 9
            else:
                self.state = 8
        # /* comment */ state
        elif self.state == 9:
            if char == '/':
                self.state = 10
            else:
                self.state = 8
        # #comment state
        elif self.state == 11:
            if char == '\n':
                self.state = 12
            else:
                self.state = 11
        # WHITESPACE state
        elif self.state == 13:
            self.lineno += int(char == '\n')
            if char in WHITESPACES:
                self.state = 13
            else:
                self.state = 21
        # */** state
        elif self.state == 15:
            if char == '*':
                self.state = 16
            elif char == '/':
                return LexicalError.UNMATCHED_COMMENT
            elif char in WHITESPACES or char in ['/', '#'] or char.isalnum():
                self.state = 17
            else:
                return LexicalError.INVALID_INPUT
        # =/== state
        elif self.state == 18:
            if char == '=':
                self.state = 19
            elif char in WHITESPACES or char in SINGLE_SYMBOLS or char in ['*', '/', '#'] or char.isalnum():
                self.state = 20
            else:
                return LexicalError.INVALID_INPUT

    def install_id(self, token: str) -> bool:
        if token in self.symbols:
            return False
        self.symbols.append(token)
        return True

    def check_final_states(self):
        # Number with dot final state
        if self.state == 4:
            self.end_cursor -= 1
            return TokenType.NUMBER
        # ID, Keyword final state
        elif self.state == 6:
            self.end_cursor -= 1
            token = self.code[self.start_cursor:self.end_cursor]
            if token in KEYWORDS:
                return TokenType.KEYWORD
            else:
                self.install_id(token)
                return TokenType.ID
        # /* comment */ final state
        elif self.state == 10:
            return TokenType.COMMENT
        # #comment final state
        elif self.state == 12:
            self.end_cursor -= 1
            return TokenType.COMMENT
        # WHITESPACE final state
        elif self.state == 21:
            self.end_cursor -= 1
            return TokenType.WHITESPACE
        # SYMBOL final state
        elif self.state in [14, 16, 19]:
            return TokenType.SYMBOL
        # SYMBOL final state (curser back)
        elif self.state in [17, 20]:
            self.end_cursor -= 1
            return TokenType.SYMBOL

    def log_error(self, error):
        invalid_string = self.code[self.start_cursor:self.end_cursor]
        if error == LexicalError.INVALID_INPUT:
            self.errors[self.lineno].append((invalid_string, error.value))
        elif error == LexicalError.UNCLOSED_COMMENT:
            self.errors[self.lineno].append(
                (f'{invalid_string[:10]}...', error.value))
        elif error == LexicalError.UNMATCHED_COMMENT:
            self.errors[self.lineno].append((invalid_string, error.value))
        elif error == LexicalError.INVALID_NUMBER:
            self.errors[self.lineno].append((invalid_string, error.value))

    @staticmethod
    def general_to_string(dict_data) -> str:
        result = ""
        if len(data_dict) == 0: # need another function
            return "There is no lexical error."
        for key, value in dict_data.items():
            string = (' '.join(map(str, value))).replace("\'", "")
            result += f"{key}.\t{string}\n"
        return result

    @staticmethod
    def symbols_to_string(list_data) -> str:
        result = ""
        count = 1
        for symbol in list_data:
            result += f"{count}.\t{symbol}\n"
            count += 1
        return result

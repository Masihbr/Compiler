import enum
import pprint
from collections import defaultdict


class TokenType(enum.Enum):
    NUMBER = 1
    ID_KEYWORD = 2
    SYMBOL = 3
    COMMENT = 4
    WHITESPACE = 5


class LexicalError(enum.Enum):
    INVALID_INPUT = 'Invalid input'
    UNCLOSED_COMMENT = 'Unclosed comment'
    UNMATCHED_COMMENT = 'Unmatched comment'
    INVALID_NUMBER = 'Invalid number'


WHITESPACES = [' ', '\n', '\r', '\t', '\v', '\f']
SINGLE_SYMBOLS = [';', ':', ',', '[', ']', '(', ')', '+', '-', '<']


class Scanner:
    input_filename = 'input.txt'

    def __init__(self):
        with open(self.input_filename, 'r') as input_file:
            self.code = input_file.read()

        self.start_line = 1
        self.end_line = 1
        self.start_cursor = 0
        self.end_cursor = 0

        self.state = 0

        self.tokens = defaultdict(list)
        self.errors = defaultdict(list)

    def get_next_token(self):
        while self.start_cursor < len(self.code):
            char = self.code[self.end_cursor]
            self.end_cursor += 1

            error = self.set_next_state(char)
            if error:
                self.log_error(error)
                self.start_cursor = self.end_cursor
                self.start_line = self.end_line
                self.state = 0

            token_type = self.check_final_states()
            if token_type:
                token = self.code[self.start_cursor:self.end_cursor]
                if token_type not in [TokenType.WHITESPACE, TokenType.COMMENT]:
                    self.tokens[self.start_line].append((token_type, token))
                self.start_cursor = self.end_cursor
                self.start_line = self.end_line
                self.state = 0
                return token_type, token

        if self.state == 8:
            self.log_error(LexicalError.UNCLOSED_COMMENT)

        pprint.pprint(self.tokens)
        pprint.pprint(self.errors)

    def set_next_state(self, char):
        if self.state == 0:
            if char.isdigit():
                self.state = 1
            elif char.isalpha():
                self.state = 5
            elif char == '/':
                self.state = 7
            elif char == '#':
                self.state = 11
            elif char in WHITESPACES:
                self.state = 13
            elif char in SINGLE_SYMBOLS:
                self.state = 14
            elif char == '*':
                self.state = 15
            elif char == '=':
                self.state = 18
            else:
                return LexicalError.INVALID_INPUT
        elif self.state == 1:
            if char.isdigit():
                self.state = 1
            elif char == '.':
                self.state = 2
            elif char in WHITESPACES or char in SINGLE_SYMBOLS or char in ['*', '=', '/', '#']:
                self.state = 4
            else:
                return LexicalError.INVALID_NUMBER
        elif self.state == 2:
            if char.isdigit():
                self.state = 3
            else:
                return LexicalError.INVALID_NUMBER
        elif self.state == 3:
            if char.isdigit():
                self.state = 3
            elif char in WHITESPACES or char in SINGLE_SYMBOLS or char in ['*', '=', '/', '#']:
                self.state = 4
            else:
                return LexicalError.INVALID_NUMBER
        elif self.state == 5:
            if char.isalnum():
                self.state = 5
            elif char in WHITESPACES or char in SINGLE_SYMBOLS or char in ['*', '=', '/', '#']:
                self.state = 6
            else:
                return LexicalError.INVALID_INPUT
        elif self.state == 7:
            if char == '*':
                self.state = 8
            else:
                self.end_cursor -= 1
                return LexicalError.INVALID_INPUT
        elif self.state == 8:
            if char == '*':
                self.state = 9
            else:
                self.state = 8
        elif self.state == 9:
            if char == '/':
                self.state = 10
            else:
                self.state = 8
        elif self.state == 11:
            if char == '\n':
                self.state = 12
            else:
                self.state = 11
        elif self.state == 15:
            if char == '*':
                self.state = 16
            elif char == '/':
                return LexicalError.UNMATCHED_COMMENT
            elif char in WHITESPACES or char in ['/', '#'] or char.isalnum():
                self.state = 17
            else:
                return LexicalError.INVALID_INPUT
        elif self.state == 18:
            if char == '=':
                self.state = 19
            elif char in WHITESPACES or char in SINGLE_SYMBOLS or char in ['*', '/', '#'] or char.isalnum():
                self.state = 20
            else:
                return LexicalError.INVALID_INPUT

    def check_final_states(self):
        if self.state == 4:
            self.end_cursor -= 1
            return TokenType.NUMBER
        elif self.state == 6:
            self.end_cursor -= 1
            return TokenType.ID_KEYWORD
        elif self.state == 10:
            return TokenType.COMMENT
        elif self.state == 12:
            self.end_cursor -= 1
            return TokenType.COMMENT
        elif self.state == 13:
            if self.code[self.start_cursor:self.end_cursor] == '\n':
                self.end_line += 1
            return TokenType.WHITESPACE
        elif self.state in [14, 16, 19]:
            return TokenType.SYMBOL
        elif self.state in [17, 20]:
            self.end_cursor -= 1
            return TokenType.SYMBOL

    def log_error(self, error):
        invalid_string = self.code[self.start_cursor:self.end_cursor]
        if error == LexicalError.INVALID_INPUT:
            self.errors[self.start_line].append((invalid_string, error.value))
        elif error == LexicalError.UNCLOSED_COMMENT:
            self.errors[self.start_line].append((f'{invalid_string[:10]}...', error.value))
        elif error == LexicalError.UNMATCHED_COMMENT:
            self.errors[self.start_line].append((invalid_string, error.value))
        elif error == LexicalError.INVALID_NUMBER:
            self.errors[self.start_line].append((invalid_string, error.value))

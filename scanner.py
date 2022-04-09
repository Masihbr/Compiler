import enum


class TokenType(enum.Enum):
    NUMBER = 1
    ID_KEYWORD = 2
    SYMBOL = 3
    COMMENT = 4
    WHITESPACE = 5


class Scanner:
    input_filename = 'input.txt'

    def __init__(self):
        with open(self.input_filename, 'r') as input_file:
            self.code = input_file.read()

        self.start_line = 0
        self.end_line = 0
        self.start_cursor = 0
        self.end_cursor = 0

        self.state = 0

    def get_next_token(self):
        for char in self.code[self.start_cursor:]:
            self.end_cursor += 1
            if char == '\n':
                self.end_line += 1

            self.set_next_state(char)

            token_type = self.check_final_states()
            if token_type:
                token = self.code[self.start_cursor:self.end_cursor]
                self.start_cursor = self.end_cursor
                self.start_line = self.end_line
                self.state = 0
                return token_type, token

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
            elif char in [' ', '\n', '\r', '\t', '\v', '\f']:
                self.state = 13
            elif char in [';', ':', ',', '[', ']', '(', ')', '+', '-', '<']:
                self.state = 14
            elif char == '*':
                self.state = 15
            elif char == '=':
                self.state = 18
        elif self.state == 1:
            if char.isdigit():
                self.state = 1
            elif char == '.':
                self.state = 2
            else:
                self.state = 4
        elif self.state == 2:
            if char.isdigit():
                self.state = 3
        elif self.state == 3:
            if char.isdigit():
                self.state = 3
            else:
                self.state = 4
        elif self.state == 5:
            if char.isalnum():
                self.state = 5
            else:
                self.state = 6
        elif self.state == 7:
            if char == '*':
                self.state = 8
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
            else:
                self.state = 17
        elif self.state == 18:
            if char == '=':
                self.state = 19
            else:
                self.state = 20

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
            return TokenType.WHITESPACE
        elif self.state in [14, 16, 19]:
            return TokenType.SYMBOL
        elif self.state in [17, 20]:
            self.end_cursor -= 1
            return TokenType.SYMBOL

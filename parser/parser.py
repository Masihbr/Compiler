from collections import deque, defaultdict

from parser.parse_table import PARSE_TABLE, SYNCHRONOUS
from scanner.scanner import Scanner, TokenType


class Parser:

    def __init__(self):
        self._scanner = Scanner()

        self._parse_table = PARSE_TABLE
        self.stack = deque(['$', 'Program'])

        self._current_token_terminal = None
        self._current_token = None

        self.errors = defaultdict(list)

    @property
    def lineno(self):
        return self._scanner.lineno

    def parse(self):
        self.advance_input()
        while self.stack:
            print(self.stack, self._current_token_terminal)
            if self._current_token_terminal == TokenType.EOF:
                break
            if self.stack[-1] not in self._parse_table.keys():
                if self.stack[-1] != self._current_token_terminal:
                    self.errors[self.lineno].append(
                        f'#{self.lineno} : syntax error, missing {self.stack[-1]}')
                    self.stack.pop()
                    continue

                self.stack.pop()
                self.advance_input()
                continue

            try:
                stack_top = self.stack[-1]
                grammar = self._parse_table[stack_top][self._current_token_terminal]

                self.stack.pop()
                if grammar == SYNCHRONOUS:
                    self.errors[self.lineno].append(
                        f'#{self.lineno} : syntax error, missing {self.stack[-1]} on line {self.lineno}')
                    pass
                if grammar is not None:
                    self.stack.extend(reversed(grammar.split()))
            except KeyError:
                self.errors[self.lineno].append(
                    f'#{self.lineno} : syntax error, illegal {self._current_token_terminal}')
                self.advance_input()

    def advance_input(self):
        self._current_token = self._scanner.get_next_token()
        if self._current_token[0] in [TokenType.WHITESPACE, TokenType.COMMENT]:
            self.advance_input()
        if self._current_token[0] in [TokenType.ID, TokenType.NUMBER]:
            self._current_token_terminal = self._current_token[0].value
        else:
            self._current_token_terminal = self._current_token[1]

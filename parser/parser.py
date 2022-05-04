from collections import deque

from parser.parse_table import PARSE_TABLE, SYNCHRONOUS
from scanner.scanner import Scanner, TokenType


class Parser:

    def __init__(self):
        self._scanner = Scanner()

        self._parse_table = PARSE_TABLE
        self.stack = deque(['$', 'Program'])

        self._current_token_terminal = None
        self._current_token = None

    def parse(self):
        self.advance_input()
        while self.stack:
            print(self.stack, self._current_token_terminal)
            if self._current_token_terminal == TokenType.EOF:
                break
            if self.stack[-1] not in self._parse_table.keys():
                if self.stack[-1] != self._current_token_terminal:
                    # TODO: ERR
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
                    # TODO: ERR
                    pass
                if grammar is not None:
                    self.stack.extend(reversed(grammar.split()))
            except KeyError:
                # TODO: ERR
                self.advance_input()

    def advance_input(self):
        self._current_token = self._scanner.get_next_token()
        if self._current_token[0] in [TokenType.WHITESPACE, TokenType.COMMENT]:
            self.advance_input()
        if self._current_token[0] in [TokenType.ID, TokenType.NUMBER]:
            self._current_token_terminal = self._current_token[0].value
        else:
            self._current_token_terminal = self._current_token[1]

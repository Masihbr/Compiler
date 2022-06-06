from collections import deque, defaultdict

from anytree import Node, RenderTree

from codegen.codegen import CodeGenerator
from parser.parse_table import PARSE_TABLE, SYNCHRONOUS
from parser.symbol_table import SymbolTable
from scanner.scanner import Scanner, TokenType
from utils.file_handler import write_all


class Parser:
    def __init__(self):
        self._symbol_table = SymbolTable()
        self._code = CodeGenerator(self._symbol_table)
        self._scanner = Scanner()
        self._parse_table = PARSE_TABLE
        self._stack = deque(['$', 'Program'])
        self._root = Node('Program')
        self._tree = deque([Node('$', parent=self._root), self._root])
        self._current_token = None
        self._declaration_lexeme = ''
        self._errors = defaultdict(list)
        self._next = False

    @property
    def lineno(self):
        return self._scanner.lineno

    @property
    def terminal(self):
        if self._current_token[0] in [TokenType.ID, TokenType.NUMBER]:
            return self._current_token[0].value
        else:
            return self._current_token[1]

    @property
    def lexeme(self):
        return self._current_token[1]

    def parse(self):
        self.advance_input()
        _continue = True
        while self._stack and _continue:
            if self._stack[-1].startswith('#'):  # TODO comments which start with #
                self.codegen()
            else:
                _continue = self.codeparse()

        write_all(filename='symbol_table', string=str(self._symbol_table))
        write_all(filename='parse_tree', string=str(RenderTree(self._root, childiter=reversed).by_attr()))
        write_all(filename='syntax_errors', string=self.errors_to_string())
        write_all(filename='output', string=self._code.get_program_block())

    def advance_input(self):
        self._current_token = self._scanner.get_next_token()
        if self._current_token[0] == TokenType.ID:
            self._declaration_lexeme = self._current_token[1]
            self._symbol_table.add_symbol(lexeme=self._declaration_lexeme, line=self.lineno)
            self._next = True
        elif self._current_token[1] == '=' and self._next:
            if self._symbol_table.add_symbol(lexeme=self._declaration_lexeme, line=self.lineno, is_def=True):
                self._code.generate('#replace', input=self._declaration_lexeme)
        if self._current_token[0] in [TokenType.WHITESPACE, TokenType.COMMENT]:
            self.advance_input()
        if self._current_token[1] != self._declaration_lexeme:
            self._next = False

    def codegen(self) -> None:
        action_symbol = self._stack.pop()
        # print(self.lineno, action_symbol)
        # pprint(self._code.get_status())
        # print(f'{"--":-^48}')
        self._code.generate(action_symbol=action_symbol, input=self.lexeme)

    def codeparse(self) -> bool:
        stack_top = self._stack[-1]
        tree_top = self._tree[-1]
        if stack_top in self._parse_table.keys():
            if self.terminal not in self._parse_table[stack_top].keys():  # empty (1)
                if self.terminal == TokenType.EOF.value and stack_top != TokenType.EOF.value:
                    self.handle_unexpected_eof()
                    return False
                self.handle_empty()
                return True

            grammar = self._parse_table[stack_top][self.terminal]
            self.pop_stacks()

            if grammar and len(grammar) > 1 and not grammar[0]:  # (EPSILON, #action) situations
                Node('epsilon', parent=tree_top)
                grammar = tuple(filter(lambda x: x, grammar))

            if grammar == SYNCHRONOUS:  # synch (2)
                self.handle_synch(stack_top, tree_top)
            elif not grammar:
                Node('epsilon', parent=tree_top)
            else:  # Non-Terminal match
                self.handle_non_terminal(tree_top, grammar)
        else:
            if stack_top != self.terminal:  # mismatch (3)
                self.handle_mismatch()
            else:  # Terminal match
                tree_top.name = '$' if self._current_token[1] == TokenType.EOF.value else \
                    f'({self._current_token[0].value}, {self._current_token[1]})'
                self.pop_stacks()
                self.advance_input()
        return True

    def pop_stacks(self):
        self._stack.pop()
        self._tree.pop()

    def handle_non_terminal(self, tree_top, grammar):
        grammar_reversed = grammar[::-1]
        children = [Node(child, parent=tree_top)
                    for child in grammar_reversed if not child.startswith('#')]
        self._stack.extend(grammar_reversed)
        self._tree.extend(children)

    def handle_unexpected_eof(self):
        self._errors[self.lineno].append(
            f'#{self.lineno} : syntax error, Unexpected EOF')
        self.clear_tree()

    def handle_empty(self):
        self._errors[self.lineno].append(
            f'#{self.lineno} : syntax error, illegal {self.terminal}')
        self.advance_input()

    def handle_synch(self, stack_top, node):
        self.remove_node(node)
        self._errors[self.lineno].append(
            f'#{self.lineno} : syntax error, missing {stack_top} on line {self.lineno}')

    def handle_mismatch(self):
        self._errors[self.lineno].append(
            f'#{self.lineno} : syntax error, missing {self._stack[-1]}')
        self.remove_node(self._tree[-1])
        self.pop_stacks()

    @staticmethod
    def remove_node(node):
        parent = node.parent
        children = list(parent.children)
        children.remove(node)
        parent.children = children

    def clear_tree(self):
        while len(self._tree) > 0:
            self.remove_node(self._tree[-1])
            self._tree.pop()

    def errors_to_string(self):
        if len(self._errors) == 0:
            return 'There is no syntax error.'
        result = ''
        for _, value in self._errors.items():
            for item in value:
                result += f'{item}\n'
        return result

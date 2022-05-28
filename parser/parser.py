from collections import deque, defaultdict
from tokenize import Token
from parser.parse_table import PARSE_TABLE, SYNCHRONOUS
from parser.symbol_table import SymbolTable
from utils.file_handler import write_all
from scanner.scanner import Scanner, TokenType
from anytree import Node, RenderTree


class Parser:
    def __init__(self):
        self._symbol_table = SymbolTable()
        self._scanner = Scanner()
        self._parse_table = PARSE_TABLE
        self._stack = deque(['$', 'Program'])
        self._root = Node('Program')
        self._tree = deque([Node('$', parent=self._root), self._root])
        self._current_token = None
        self._errors = defaultdict(list)

    @property
    def lineno(self):
        return self._scanner.lineno

    @property
    def terminal(self):
        if self._current_token[0] in [TokenType.ID, TokenType.NUMBER]:
            return self._current_token[0].value
        else:
            return self._current_token[1]

    def pop_stacks(self):
        self._stack.pop()
        self._tree.pop()

    def remove_node(self, node):
        parent = node.parent
        children = list(parent.children)
        children.remove(node)
        parent.children = children

    def clear_tree(self):
        while len(self._tree) > 0:
            self.remove_node(self._tree[-1])
            self._tree.pop()

    def parse(self):
        self.advance_input()
        while self._stack:
            stack_top = self._stack[-1]
            tree_top = self._tree[-1]
            if stack_top in self._parse_table.keys():
                if self.terminal not in self._parse_table[stack_top].keys(): # empty (1)
                    if self.terminal == TokenType.EOF.value and self._stack[-1] != TokenType.EOF.value:
                        self.handle_unexpected_eof()
                        break
                    self.handle_empty()
                    continue
                
                grammar = self._parse_table[stack_top][self.terminal]
                self.pop_stacks()
                
                if grammar == SYNCHRONOUS:  # synch (2)
                    self.handle_synch(stack_top, tree_top)
                elif not grammar:
                    Node('epsilon', parent=tree_top)
                else: # Non-Terminal match
                    grammar_reversed = grammar[::-1]
                    children = [Node(child, parent=tree_top)
                                for child in grammar_reversed]
                    self._stack.extend(grammar_reversed)
                    self._tree.extend(children)
            else:
                if stack_top != self.terminal:  # mismatch (3)
                    self.handle_mismatch()
                else: # Terminal match
                    tree_top.name = '$' if self._current_token[1] == TokenType.EOF.value else \
                        f'({self._current_token[0].value}, {self._current_token[1]})'
                    self.pop_stacks()
                    self.advance_input()
        
        write_all(filename='symbol_table', string=str(self._symbol_table))
        write_all(filename='parse_tree', string=str(RenderTree(self._root, childiter=reversed).by_attr()))
        write_all(filename='syntax_errors', string=self.errors_to_string())

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

    def advance_input(self):
        self._current_token = self._scanner.get_next_token()
        if self._current_token[0] == TokenType.ID:
            self._symbol_table.add_symbol(lexeme=self._current_token[1], line=self.lineno)
        if self._current_token[0] in [TokenType.WHITESPACE, TokenType.COMMENT]:
            self.advance_input()

    def errors_to_string(self):
        if len(self._errors) == 0:
            return 'There is no syntax error.'
        result = ''
        for _, value in self._errors.items():
            for item in value:
                result += f'{item}\n'
        return result

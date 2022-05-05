from collections import deque, defaultdict
from tokenize import Token

from parser.parse_table import PARSE_TABLE, SYNCHRONOUS
from scanner.file_handler import write_all
from scanner.scanner import Scanner, TokenType
from anytree import Node, RenderTree

class Parser:

    def __init__(self):
        self._scanner = Scanner()

        self._parse_table = PARSE_TABLE
        self.stack = deque(['$', 'Program'])
        self.root = Node('Program')
        end = Node('$', parent = self.root)
        self.tree = deque([end, self.root])
        self._current_token_terminal = None
        self._current_token = None

        self.errors = defaultdict(list)

    @property
    def lineno(self):
        return self._scanner.lineno

    def remove_node(self, node):
        parent = node.parent
        children = list(parent.children)
        children.remove(node)
        parent.children = children
    
    def parse(self):
        self.advance_input()
        while self.stack:
            # print(self.stack, self._current_token_terminal, self.lineno)
            if self._current_token_terminal == TokenType.EOF.value:
                break
            if self.stack[-1] not in self._parse_table.keys():
                if self.stack[-1] != self._current_token_terminal:
                    # print('\ntoken match', self.stack, self.lineno, '\n')
                    self.errors[self.lineno].append(
                        f'#{self.lineno} : syntax error, missing {self.stack[-1]}')
                    self.stack.pop()
                    self.remove_node(self.tree[-1])
                    self.tree.pop()
                    continue
                
                self.stack.pop()
                self.tree[-1].name = f"({self._current_token[0].value}, {self._current_token[1]})" if self._current_token[1] != '$' else '$'
                self.tree.pop()
                self.advance_input()
                continue

            try:
                stack_top = self.stack[-1]
                parent = self.tree[-1]
                grammar = self._parse_table[stack_top][self._current_token_terminal]
                self.stack.pop()
                self.tree.pop()
                if grammar == SYNCHRONOUS:
                    self.remove_node(parent)
                    self.errors[self.lineno].append(
                        f'#{self.lineno} : syntax error, missing {stack_top} on line {self.lineno}')
                elif grammar is not None:
                    grammar_split = grammar.split()
                    temp = list(reversed(grammar_split))
                    children = [Node(item, parent=parent) for item in temp]
                    self.stack.extend(temp)
                    self.tree.extend(children)
                else:
                    Node('epsilon', parent=parent)
            except KeyError:
                self.errors[self.lineno].append(
                    f'#{self.lineno} : syntax error, illegal {self._current_token_terminal}')
                self.advance_input()
                
        write_all(filename='parse_tree', string=str(RenderTree(self.root, childiter=reversed).by_attr())) 
        write_all(filename='syntax_errors', string=self.errors_to_string())           
        
    def advance_input(self):
        self._current_token = self._scanner.get_next_token()
        if self._current_token[0] in [TokenType.WHITESPACE, TokenType.COMMENT]:
            self.advance_input()
        if self._current_token[0] in [TokenType.ID, TokenType.NUMBER]:
            self._current_token_terminal = self._current_token[0].value
        else:
            self._current_token_terminal = self._current_token[1]
            
    def errors_to_string(self):
        if len(self.errors) == 0:
            return 'There is no syntax error.'
        result = ''
        for _, value in self.errors.items():
            for item in value:
                result += f'{item}\n'
        return result

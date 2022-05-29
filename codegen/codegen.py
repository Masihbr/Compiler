from collections import deque
import warnings

from parser.symbol_table import SymbolTable


class CodeGenerator:
    def __init__(self, symbol_table: SymbolTable = None) -> None:
        self._program_block = list()
        self._semantic_stack = deque()
        self._symbol_table = symbol_table
        self.print_flag = False
        self._generator = {
            '#pid': self.pid,
            '#pnum': self.pnum,
            '#assign': self.assign,
            '#func_call_finish': self.func_call_finish,
        }

    def generate(self, action_symbol: str, input: str):
        try:
            if action_symbol in {'#pid', '#pnum'}:  # set of actions which need input for operation
                self._generator[action_symbol](input)
            else:
                self._generator[action_symbol]()
        except KeyError:
            warnings.warn(f'Sorry {action_symbol} not implemented yet.')

    def pid(self, lexeme):
        addr = self._symbol_table.find_addr(lexeme)
        if addr:
            self._semantic_stack.append(addr)
        else:
            raise Exception(f'Address of {lexeme} not found.')

    def pnum(self, number):
        self._semantic_stack.append("#" + number)
    
    def assign(self):
        lhs = self._semantic_stack.pop()
        rhs = self._semantic_stack.pop()
        self._program_block.append(self.code('ASSIGN', lhs, rhs))

    def func_call_finish(self):
        if self._symbol_table.find_lexeme(self._semantic_stack[-2]) == 'output':
            out, _ = self._semantic_stack.pop(), self._semantic_stack.pop()
            self._program_block.append(self.code('PRINT', out))

    
    def code(self, action: str = '', *args) -> str:
        args_len = len(args)
        if args_len > 3:
            raise Exception('Wrong inputs')
        if action in {'ADD', 'MULT', 'SUB', 'EQ', 'LT'} and args_len == 3:
            return f'({action}, {args[0]}, {args[1]}, {args[2]})'
        elif action in {'ASSIGN', 'JPF'} and args_len == 2:
            return f'({action}, {args[0]}, {args[1]}, )'
        elif action in {'PRINT', 'JP'} and args_len == 1:
            return f'({action}, {args[0]}, , )'
        else:
            raise Exception(
                f'Number of inputs {args_len} does not match action {action}')

    def get_program_block(self) -> str:
        line = 0
        res = ''
        for code in self._program_block:
            res += f'{line}\t{code}\n'
            line += 1
        return res
        

from collections import deque
import warnings

from parser.symbol_table import SymbolTable


class TempManager:
    def __init__(self, start_address:int=1500, step:int=4):
        self.current_temp = start_address
        self._step = step

    def get_temp(self):
        addr = self.current_temp
        self.current_temp += self._step
        return addr

    def get_arr_temp(self, arr_len):
        self.current_temp += self._step
        start_point = self.current_temp
        self.current_temp += self._step * (arr_len - 1)
        return start_point

class CodeGenerator:
    def __init__(self, symbol_table: SymbolTable = None) -> None:
        self._program_block = list()
        self._semantic_stack = deque()
        self._temp_generator = TempManager()
        self._symbol_table = symbol_table
        self._generator = {
            '#pid': self.pid,
            '#pnum': self.pnum,
            '#assign': self.assign,
            '#func_call_finish': self.func_call_finish,
            '#save': self.save,
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

    def save(self):
        self._program_block.append(self.code())
        self._semantic_stack.append(len(self._program_block))
    
    def jpf_save(self):
        pass
        self.save()
    
    def jp(self):
        pass
        
    def jpf(self):
        pass
    
    def comp_op(self, input:str):
        if input == '==':
            self._semantic_stack.append('EQ')
        elif input == '<':
            self._semantic_stack.append('LT')
        else:
            raise Exception(f'What the hell is {input}')
    
    def comp(self, input:str):
        rhs = self._semantic_stack.pop()
        action = self._semantic_stack.pop()
        lhs = self._semantic_stack.pop()
        temp = self._temp_generator.get_temp()
        self._program_block.append(self.code(action, rhs, lhs, temp))
        self._semantic_stack.append(temp)
            
    def code(self, action: str = '', *args) -> str:
        args_len = len(args)
        if len(action) == 0:
            return f'( , , , )'
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
        

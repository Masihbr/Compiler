from ast import Index
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
        self._first_func_seen = True # set to false after seeing the first function other than main
        self._generator = {
            '#pid': self.pid,
            '#pnum': self.pnum,
            '#assign': self.assign,
            '#func_call_finish': self.func_call_finish,
            '#save': self.save,
            '#save_func': self.save_func,
            '#jpf': self.jpf,
            '#jpf_save': self.jpf_save,
            '#jp': self.jp,
            '#comp': self.comp,
            '#comp_op': self.comp_op,
            '#set_func_start': self.set_func_start,
            '#jump_main': self.jump_main,
            '#func_def_finish': self.func_def_finish,
        }

    @property
    def pb_len(self):
        return len(self._program_block)
    
    def generate(self, action_symbol: str, input: str):
        try:
            if action_symbol in {'#pid', '#pnum', '#comp_op'}:  # set of actions which need input for operation
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
        self._semantic_stack.append(self.pb_len)
        self._program_block.append(self.code())
    
    def jpf_save(self):
        self.jpf()
        self.save()
    
    def jp(self):
        jump_address = self._semantic_stack.pop()
        current_address = self.pb_len - 1
        self._program_block[jump_address] = self.code('JP', current_address) 
        
    def jpf(self):
        jump_address = self._semantic_stack.pop()
        jump_condition = self._semantic_stack.pop()
        current_address = self.pb_len + 1
        self._program_block[jump_address] = self.code('JPF', jump_condition, current_address)
    
    def comp_op(self, input:str):
        if input == '==':
            self._semantic_stack.append('EQ')
        elif input == '<':
            self._semantic_stack.append('LT')
        else:
            raise Exception(f'What the hell is {input}')
    
    def comp(self):
        rhs = self._semantic_stack.pop()
        action = self._semantic_stack.pop()
        lhs = self._semantic_stack.pop()
        temp = self._temp_generator.get_temp()
        self._program_block.append(self.code(action, lhs, rhs, temp))
        self._semantic_stack.append(temp)
         
    def set_func_start(self) -> None:
        self._symbol_table.set_pb_line(self.pb_len)
    
    def jump_main(self) -> None:
        try: # if code only has the main function no need for jump
            self._program_block[self._semantic_stack.pop()] = self.code('JP', self._symbol_table.get_pb_line(lexeme='main'))
        except IndexError:
            Warning('Only main function present.')
            return
    
    def save_func(self) -> None:
        func_address = self._semantic_stack.pop()
        if  self._symbol_table.find_lexeme(func_address) != 'main' \
            and self._first_func_seen: # don't save main - don't save after first function
            self.save()
            self._first_func_seen = False
        self._semantic_stack.append(func_address)
    
    def func_def_finish(self) -> None:
        self._semantic_stack.pop()
      
    def code(self, action: str = '', *args) -> str:
        args_len = len(args)
        if action == '':
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
    
    def get_status(self):
        return {'semantic_stack': self._semantic_stack,
                'program_block': self._program_block}
        

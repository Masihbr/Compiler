import warnings
from collections import deque

from codegen.program_block import ProgramBlock
from codegen.semantic_error import SemanticError, SemanticErrorHandler
from codegen.stack import Stack
from codegen.temp_manager import TempManager
from parser.symbol_table import SymbolTable
from dataclasses import dataclass

@dataclass
class LexemeStatus:
    lexeme: str = ''
    is_same_scope: bool = False
    is_found: bool = False

class CodeGenerator:
    def __init__(self, symbol_table: SymbolTable = None) -> None:
        self._program_block = ProgramBlock()
        self._semantic_stack = deque()
        self._temp_manager = TempManager()
        self._func_stack = Stack(self._program_block, self._temp_manager)
        self._symbol_table = symbol_table
        self._first_func_seen = True  # set to false after seeing the first function other than main
        self._unknown_func_active = False
        self._while_stack = deque()  # stack of tuples: [(while address, list of breaks),...]
        self._lexeme_status = LexemeStatus('', False, False)
        self._step = 4
        self.lineno = 0
        self.globals = set()
        self.error_handler = SemanticErrorHandler()
        self._args_count = deque()
        self._generator = {
            '#pid': self.pid,
            '#pnum': self.pnum,
            '#pparam': self.pparam,
            '#pfunc': self.pfunc,
            '#check_func': self.check_func,
            '#psym': self.psym,
            '#add_sym': self.add_sym,
            '#check_sym': self.check_sym,
            '#assign': self.assign,
            '#label': self.label,
            '#save': self.save,
            '#save_func': self.save_func,
            '#jpf': self.jpf,
            '#jpf_save': self.jpf_save,
            '#jp': self.jp,
            '#comp': self.comp,
            '#comp_op': self.comp_op,
            '#set_func_start': self.set_func_start,
            '#jump_main': self.jump_main,
            '#func_def_start': self.func_def_start,
            '#push_zero': self.push_zero,
            '#func_def_finish': self.func_def_finish,
            '#func_call_start': self.func_call_start,
            '#func_call_finish': self.func_call_finish,
            '#add_arg': self.add_arg,
            '#pop_func_address': self.pop_func_address,
            '#add': self.add,
            '#sub': self.sub,
            '#mult': self.mult,
            '#power': self.power,
            '#while': self._while,
            '#break': self._break,
            '#continue': self._continue,
            '#pop': self.pop,
            '#arr_init': self.arr_init,
            '#parr': self.parr,
            '#arr_len': self.arr_len,
            '#index': self.index,
            '#replace': self.replace,
            '#global': self._global,
            '#has_return_value': self.has_return_value,
            '#check_void': self.check_void,
        }

    @property
    def program_block(self):
        return self._program_block.codes

    @property
    def pb_len(self):
        return len(self.program_block)

    @property
    def code(self):
        return self._program_block.code

    def generate(self, action_symbol: str, input: str) -> None:
        try:
            if action_symbol in {'#pid', '#pnum', '#pparam', '#pfunc', '#comp_op',
                                 '#replace', '#psym', '#global'}:  # set of actions which need input for operation
                self._generator[action_symbol](input)
            else:
                self._generator[action_symbol]()
        except KeyError:
            warnings.warn(f'Sorry {action_symbol} not implemented yet.')

    def pop(self) -> None:
        self._semantic_stack.pop()

    def pid(self, lexeme) -> None:
        addr = self._symbol_table.find_addr(lexeme)
        if addr:
            self._semantic_stack.append(addr)
        else:
            self.error_handler.add(SemanticError.ID_NOT_DEFINED, self.lineno, id=lexeme)
            self._semantic_stack.append(-1) # push dummy invalid address in stack 

    def psym(self, lexeme) -> None:
        addr = self._symbol_table.find_addr(lexeme)
        self._lexeme_status.lexeme = lexeme
        if addr:
            self._semantic_stack.append(addr)
            self._lexeme_status.is_found = True
            self._lexeme_status.is_same_scope = self._symbol_table.is_symbol_current_scope(addr=addr)
        else:
            self._lexeme_status.is_found, self._lexeme_status.is_same_scope = False, False            
    
    def add_sym(self) -> None:
        if self._lexeme_status.is_found and self._lexeme_status.is_same_scope:
            self._lexeme_status = LexemeStatus()
            return
        elif not self._lexeme_status.is_found:
            symbol = self._symbol_table.add_symbol(lexeme=self._lexeme_status.lexeme, line=self.lineno)
            self._semantic_stack.append(symbol.address)
        elif not self._lexeme_status.is_same_scope and self._lexeme_status.lexeme not in self.globals:
            symbol = self._symbol_table.add_symbol(lexeme=self._lexeme_status.lexeme, line=self.lineno, force=True)
            self._semantic_stack.pop()
            self._semantic_stack.append(symbol.address)
        self._lexeme_status = LexemeStatus()    
    
    def check_sym(self) -> None:
        if not self._lexeme_status.is_found:
            self.error_handler.add(SemanticError.ID_NOT_DEFINED, self.lineno, id=self._lexeme_status.lexeme)
            self._semantic_stack.append(-1) # push dummy address as func address
    
    def pnum(self, number) -> None:
        temp = self._temp_manager.get_temp()
        self.program_block.append(self.code('ASSIGN', f'#{number}', temp))
        self._semantic_stack.append(temp)

    def pparam(self, lexeme: str) -> None:
        self._symbol_table.add_symbol(lexeme=lexeme, category='param', line=self.lineno)
        self._symbol_table.inc_args()
        self.pid(lexeme=lexeme)

    def pfunc(self, lexeme: str) -> None:
        self._symbol_table.add_symbol(lexeme=lexeme, category='func', line=self.lineno, force=True)
        self.pid(lexeme=lexeme)

    def check_func(self) -> None:
        if not self._symbol_table.is_last_func_valid():
            func = self._symbol_table.get_symbol(category='func')
            self.error_handler.add(SemanticError.OVERLOADING, lineno=func.line, id=func.lexeme)
            self._symbol_table.remove_last_func()
    
    def assign(self) -> None:
        rhs = self._semantic_stack.pop()
        lhs = self._semantic_stack.pop()
        self.program_block.append(self.code('ASSIGN', rhs, lhs))

    def label(self) -> None:
        self._while_stack.append((self.pb_len, []))

    def save(self) -> None:
        self._semantic_stack.append(self.pb_len)
        self.program_block.append(self.code())

    def jpf_save(self) -> None:
        self.jpf(inc=1)
        self.save()

    def jp(self) -> None:
        jump_address = self._semantic_stack.pop()
        current_address = self.pb_len
        self.program_block[jump_address] = self.code('JP', current_address)

    def jpf(self, inc: int = 0) -> None:
        jump_address = self._semantic_stack.pop()
        jump_condition = self._semantic_stack.pop()
        current_address = self.pb_len + inc
        self.program_block[jump_address] = self.code('JPF', jump_condition, current_address)

    def comp_op(self, input: str):
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
        if not lhs or not rhs:
            self._semantic_stack.append(-1) # push dummy invalid address in stack as result 
            return
        temp = self._temp_manager.get_temp()
        self.program_block.append(self.code(action, lhs, rhs, temp))
        self._semantic_stack.append(temp)

    def set_func_start(self) -> None:
        self._symbol_table.set_pb_line(self.pb_len)

    def jump_main(self) -> None:
        try:  # if code only has the main function no need for jump
            main_pb_line = self._symbol_table.get_pb_line(lexeme='main')
            if not main_pb_line:
                self.error_handler.add(SemanticError.MAIN_MISSING, self.lineno)
                return
            self.program_block[self._semantic_stack.pop()] = self.code('JP', main_pb_line)
        except IndexError:
            Warning('Only main function present.')
            return

    def save_func(self) -> None:
        self._symbol_table.scope_push()
        func_address = self._semantic_stack.pop()
        if self._symbol_table.find_lexeme(func_address) != 'main' \
                and self._first_func_seen:  # don't save main - don't save after first function
            self.save()
            self._first_func_seen = False
        self._semantic_stack.append(func_address)

    def func_def_start(self) -> None:
        args_count = self._symbol_table.get_func_args_count().pop()
        args_start = 2  # args start point in stack
        for offset in range(args_start, args_start + args_count):  #
            arg = self._semantic_stack.pop()
            temp = self._func_stack.access(offset)
            self.program_block.append(self.code('ASSIGN', temp, arg))

    def push_zero(self) -> None:
        self._semantic_stack.append('#0')  # return value of func is void if no return expr

    def has_return_value(self) -> None:
        self._symbol_table.set_has_return_value()

    def func_def_finish(self) -> None:
        if self._symbol_table.find_lexeme(self._semantic_stack[-2]) == 'main':
            self._semantic_stack.pop()
            return

        return_value = self._semantic_stack.pop()
        self._func_stack.push(return_value)  # may have problem with order
        return_address = self._func_stack.access(2)
        self.program_block.append(self.code('JP', f'@{return_address}'))

    def pop_func_address(self) -> None:
        self._symbol_table.scope_pop()
        addr = self._semantic_stack.pop()  # pop func addr
        self._symbol_table.kill_block(addr)
        self.globals = set() # empty global set

    def func_call_start(self) -> None:
        func_name = self._symbol_table.find_lexeme(self._semantic_stack[-1])
        if not func_name: # problematic
            self._unknown_func_active = True
        self._args_count.append(0)

    def add_arg(self) -> None:
        if self._unknown_func_active:
            self._semantic_stack.pop()
            return
        
        args_count = self._args_count.pop()
        arg = self._semantic_stack.pop()
        self._func_stack.push(arg)
        self._args_count.append(args_count + 1)

    def func_call_finish(self) -> None:
        if self._unknown_func_active:
            self._unknown_func_active = False
            return
        elif self._symbol_table.find_lexeme(self._semantic_stack[-1]) == 'output':
            out = self._func_stack.pop()
            self.program_block.append(self.code('PRINT', out))
            return
        
        assumed_func_address = self._semantic_stack.pop()
        # this func address has only matched the lexeme of func ID
        # actual func address may be different depending on number of arguments
        func_lexeme = self._symbol_table.find_lexeme(assumed_func_address)
        args_count_given = self._args_count.pop()
        possible_args_count = self._symbol_table.get_func_args_count(lexeme=func_lexeme)

        if args_count_given not in possible_args_count:
            self.error_handler.add(SemanticError.ARGS_MISMATCH, self.lineno, id=func_lexeme)
            actual_func_address = self._symbol_table.get_first_func_address(lexeme=func_lexeme)
        else:
            actual_func_address = self._symbol_table.get_func_address(lexeme=func_lexeme, args_count=args_count_given)
            
        func_pb_line = self._symbol_table.get_pb_line(addr=actual_func_address)

        current_pb_line = self.pb_len
        self._func_stack.push(f'#{current_pb_line + 3}')
        self.program_block.append(self.code('JP', func_pb_line))
        
        return_value = self._func_stack.pop() if self._symbol_table.get_has_return_value(addr=actual_func_address) else None
        self._semantic_stack.append(return_value)
        
        self._func_stack.pop()
        for _ in range(args_count_given):
            self._func_stack.pop()

    def add(self) -> None:
        self.arith('ADD')

    def sub(self) -> None:
        self.arith('SUB')

    def mult(self) -> None:
        self.arith('MULT')

    def power(self) -> None:
        temp1 = self._temp_manager.get_temp()
        temp2 = self._temp_manager.get_temp()
        r_op = self._semantic_stack.pop()
        l_op = self._semantic_stack.pop()
        if not r_op or not l_op:
            self._semantic_stack.append(-1) # push dummy invalid address in stack as result 
            return
        
        self.program_block.append(self.code('ASSIGN', '#1', temp1))
        self.program_block.append(self.code('ASSIGN', r_op, temp2))
        start = self.pb_len
        self.program_block.append(self.code('JPF', temp2, self.pb_len + 4))
        self.program_block.append(self.code('MULT', temp1, l_op, temp1))
        self.program_block.append(self.code('SUB', temp2, '#1', temp2))
        self.program_block.append(self.code('JP', start))

        self._semantic_stack.append(temp1)

    def arith(self, action: str = 'ADD') -> None:
        temp = self._temp_manager.get_temp()
        lhs = self._semantic_stack.pop()
        rhs = self._semantic_stack.pop()
        if not lhs or not rhs:
            self._semantic_stack.append(-1) # push dummy invalid address in stack as result 
            return
        
        self.program_block.append(self.code(action, rhs, lhs, temp))
        self._semantic_stack.append(temp)

    def _while(self) -> None:
        while_info = self._while_stack.pop()
        while_address = while_info[0]
        breaks = while_info[1]
        pb_address = self._semantic_stack.pop()
        jump_condition = self._semantic_stack.pop()
        jump_out_address = self.pb_len + 1
        self.program_block[pb_address] = self.code('JPF', jump_condition, jump_out_address)
        self.program_block.append(self.code('JP', while_address))
        for break_address in breaks:
            self.program_block[break_address] = self.code('JP', jump_out_address)
        self._break_count = 0

    def _break(self) -> None:
        if len(self._while_stack) == 0:
            self.error_handler.add(SemanticError.BREAK_MISSING_WHILE, self.lineno)
            return 
        self._while_stack[-1][1].append(self.pb_len)
        self.program_block.append(self.code('JP', '?'))

    def _continue(self) -> None:
        if len(self._while_stack) == 0:
            self.error_handler.add(SemanticError.CONTINUE_MISSING_WHILE, self.lineno)
            return
        while_address = self._while_stack[-1][0]
        self.program_block.append(self.code('JP', while_address))

    def arr_init(self) -> None:
        temp = self._temp_manager.get_temp()
        self.program_block.append(self.code('ASSIGN', f'#{self._temp_manager.arr_temp}', temp))
        self._semantic_stack.append(temp)
        self._semantic_stack.append(self._temp_manager.arr_temp)

    def parr(self) -> None:
        expr = self._semantic_stack.pop()
        temp = self._temp_manager.get_arr_temp()
        self.program_block.append(self.code('ASSIGN', expr, temp))

    def arr_len(self) -> None:
        arr_len = (self._temp_manager.arr_temp - self._semantic_stack.pop()) // self._step
        arr_addr = self._semantic_stack[-2]  # lhs of assign - semantic_stack[-1] contains arr start address
        self._symbol_table.set_args_cells(addr=arr_addr, count=arr_len)

    def index(self) -> None:
        arr_index = self._semantic_stack.pop()
        arr_addr = self._semantic_stack.pop()

        self._semantic_stack.append(arr_index)
        self._semantic_stack.append(f'#{self._step}')
        self.mult()

        self._semantic_stack.append(arr_addr)
        self.add()

        indexed_addr = self._semantic_stack.pop()
        self._semantic_stack.append(f'@{indexed_addr}')

    def replace(self, lexeme: str = '') -> None:
        self._semantic_stack.pop()
        self._semantic_stack.append(self._symbol_table.find_addr(lexeme=lexeme))

    def _global(self, lexeme: str = '') -> None:
        self.globals.add(lexeme)
    
    def check_void(self) -> None:
        if not self._semantic_stack[-1]:
            self.error_handler.add(SemanticError.VOID_OPERAND, self.lineno)
        
    def get_program_block(self) -> str:
        if len(self.error_handler.semantic_errors) == 0:
            return self._program_block.str_program_block()
        else:
            return 'The output code has not been generated.'

    def get_semantic_errors(self) -> str:
        return self.error_handler.get_errors_str()
    
    def get_status(self):
        return {
            'semantic_stack': self._semantic_stack,
            # 'program_block': self.program_block[-30:],
            'func_stack': self._func_stack.shadow_stack,
        }

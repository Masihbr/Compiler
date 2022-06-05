import warnings
from collections import deque

from codegen.program_block import ProgramBlock
from codegen.stack import Stack
from codegen.temp_manager import TempManager
from parser.symbol_table import SymbolTable


class CodeGenerator:
    def __init__(self, symbol_table: SymbolTable = None) -> None:
        self._program_block = ProgramBlock()
        self._semantic_stack = deque()
        self._temp_manager = TempManager()
        self._func_stack = Stack(self._program_block, self._temp_manager)
        self._symbol_table = symbol_table
        self._first_func_seen = True  # set to false after seeing the first function other than main
        self._output_func_active = False
        self._break_stack = deque()  # save breaks then fill them
        self._step = 4
        self._generator = {
            '#pid': self.pid,
            '#pnum': self.pnum,
            '#pparam': self.pparam,
            '#pfunc': self.pfunc,
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
            '#pop': self.pop,
            '#arr_init': self.arr_init,
            '#parr': self.parr,
            '#arr_len': self.arr_len,
            '#index': self.index,
            '#replace': self.replace,
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
                                 '#replace'}:  # set of actions which need input for operation
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
            raise Exception(f'Address of {lexeme} not found.')

    def pnum(self, number) -> None:
        temp = self._temp_manager.get_temp()
        self.program_block.append(self.code('ASSIGN', f'#{number}', temp))
        self._semantic_stack.append(temp)

    def pparam(self, lexeme: str) -> None:
        self._symbol_table.set_param(lexeme=lexeme)
        self.pid(lexeme=lexeme)

    def pfunc(self, lexeme: str) -> None:
        self._symbol_table.set_category(lexeme=lexeme, category='func')
        self.pid(lexeme=lexeme)

    def assign(self) -> None:
        rhs = self._semantic_stack.pop()
        lhs = self._semantic_stack.pop()
        self.program_block.append(self.code('ASSIGN', rhs, lhs))

    def label(self) -> None:
        self._semantic_stack.append(self.pb_len)

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
        temp = self._temp_manager.get_temp()
        self.program_block.append(self.code(action, lhs, rhs, temp))
        self._semantic_stack.append(temp)

    def set_func_start(self) -> None:
        self._symbol_table.set_pb_line(self.pb_len)

    def jump_main(self) -> None:
        try:  # if code only has the main function no need for jump
            self.program_block[self._semantic_stack.pop()] = self.code('JP',
                                                                       self._symbol_table.get_pb_line(lexeme='main'))
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
        args_count = self._symbol_table.get_func_args_count()
        args_start = 2  # args start point in stack
        for offset in range(args_start, args_start + args_count):  #
            arg = self._semantic_stack.pop()
            temp = self._func_stack.access(offset)
            self.program_block.append(self.code('ASSIGN', temp, arg))

    def push_zero(self) -> None:
        self._semantic_stack.append('#0')  # return value of func is 0 if no return expr

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

    def func_call_start(self) -> None:
        func_name = self._symbol_table.find_lexeme(self._semantic_stack[-1])
        if func_name == 'output':
            self._output_func_active = True

    def add_arg(self) -> None:
        if self._output_func_active:
            return

        arg = self._semantic_stack.pop()
        self._func_stack.push(arg)

    def func_call_finish(self) -> None:
        if self._output_func_active:
            out = self._semantic_stack.pop()
            self.program_block.append(self.code('PRINT', out))
            self._output_func_active = False
            return

        func_address = self._semantic_stack.pop()
        func_pb_line = self._symbol_table.get_pb_line(addr=func_address)

        current_pb_line = self.pb_len
        self._func_stack.push(f'#{current_pb_line + 3}')
        self.program_block.append(self.code('JP', func_pb_line))

        return_value = self._func_stack.pop()
        self._semantic_stack.append(return_value)
        args_count = self._symbol_table.get_func_args_count(addr=func_address)
        self._func_stack.pop()
        for _ in range(args_count):
            self._func_stack.pop()

    def add(self):
        self.arith('ADD')

    def sub(self):
        self.arith('SUB')

    def mult(self):
        self.arith('MULT')

    # TODO: x ** y doesn't work when y < 1
    def power(self):
        temp1 = self._temp_manager.get_temp()
        temp2 = self._temp_manager.get_temp()
        temp3 = self._temp_manager.get_temp()
        r_op = self._semantic_stack.pop()
        l_op = self._semantic_stack.pop()

        self.program_block.append(self.code('ASSIGN', l_op, temp1))
        self.program_block.append(self.code('ASSIGN', r_op, temp2))
        start = self.pb_len
        self.program_block.append(self.code('MULT', temp1, l_op, temp1))
        self.program_block.append(self.code('SUB', temp2, '#1', temp2))
        self.program_block.append(self.code('LT', temp2, '#2', temp3))
        self.program_block.append(self.code('JPF', temp3, start))

        self._semantic_stack.append(temp1)

    def arith(self, action: str = 'ADD'):
        temp = self._temp_manager.get_temp()
        lhs = self._semantic_stack.pop()
        rhs = self._semantic_stack.pop()
        self.program_block.append(self.code(action, rhs, lhs, temp))
        self._semantic_stack.append(temp)

    def _while(self):
        breaks = [self._break_stack.pop() for _ in range(len(self._break_stack))]
        pb_address = self._semantic_stack.pop()
        jump_condition = self._semantic_stack.pop()
        while_address = self._semantic_stack.pop()
        jump_out_address = self.pb_len + 1
        self.program_block[pb_address] = self.code('JPF', jump_condition, jump_out_address)
        self.program_block.append(self.code('JP', while_address))
        for break_address in breaks:
            self.program_block[break_address] = self.code('JP', jump_out_address)
        self._break_count = 0

    def _break(self):
        self._break_stack.append(self.pb_len)
        self.program_block.append(self.code('JP', '?'))

    def arr_init(self):
        temp = self._temp_manager.get_temp()
        self.program_block.append(self.code('ASSIGN', f'#{self._temp_manager.arr_temp}', temp))
        self._semantic_stack.append(temp)
        self._semantic_stack.append(self._temp_manager.arr_temp)

    def parr(self):
        expr = self._semantic_stack.pop()
        temp = self._temp_manager.get_arr_temp()
        self.program_block.append(self.code('ASSIGN', expr, temp))

    def arr_len(self):
        arr_len = (self._temp_manager.arr_temp - self._semantic_stack.pop()) // self._step
        arr_addr = self._semantic_stack[-2]  # lhs of assign - semantic_stack[-1] contains arr start address
        self._symbol_table.set_args_cells(addr=arr_addr, count=arr_len)

    def index(self):
        arr_index = self._semantic_stack.pop()
        arr_addr = self._semantic_stack.pop()

        self._semantic_stack.append(arr_index)
        self._semantic_stack.append(f'#{self._step}')
        self.mult()

        self._semantic_stack.append(arr_addr)
        self.add()

        indexed_addr = self._semantic_stack.pop()
        self._semantic_stack.append(f'@{indexed_addr}')

    def replace(self, lexeme: str = ''):
        self._semantic_stack.pop()
        self._semantic_stack.append(self._symbol_table.find_addr(lexeme=lexeme))

    def get_program_block(self) -> str:
        return self._program_block.str_program_block()

    def get_status(self):
        return {
            'semantic_stack': self._semantic_stack,
            # 'program_block': self.program_block[-30:],
            'func_stack': self._func_stack.shadow_stack,
        }

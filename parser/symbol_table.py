from collections import deque
from typing import Iterator


class Symbol:
    def __init__(
            self,
            lexeme: str = '',
            address: int = 0,
            category: str = 'var',
            _type: str = '',
            line: int = 0,
            scope: int = 0
    ) -> None:
        self.lexeme = lexeme
        self.address = address
        self.category = category  # {func, var, param}
        self.args_cells = 0
        self.type = _type
        self.line = line
        self.pb_line = 0
        self.scope = scope
        self.alive = True

    def __str__(self) -> str:
        return f'{self.lexeme:<10} {self.address:<10} {self.pb_line:<10} {self.category:<10} ' \
               f'{self.args_cells:<10} {self.type:<10} {self.line:<10} {self.alive:<10} {self.scope:<10}'


class SymbolTable:
    def __init__(self, start_address: int = 100, step: int = 4) -> None:
        self._current_address = start_address
        self._step = step
        self._symbols = list()
        self._scope_stack = deque()
        self.def_output()

    def def_output(self):
        self.add_symbol(lexeme='output', category='func', line=0)
    
    @property
    def alive_symbols(self) -> Iterator:
        return filter(lambda s: s.alive, reversed(self._symbols))

    def _get_symbol(self, lexeme: str = None, addr: int = None, category: str = None) -> Symbol:
        for symbol in self.alive_symbols:
            if symbol.lexeme == lexeme:
                return symbol
            elif symbol.address == addr:
                return symbol
            elif symbol.category == category:
                return symbol

    def find_addr(self, lexeme: str = '') -> int:
        symbol = self._get_symbol(lexeme=lexeme)
        return symbol.address if symbol else None

    def find_lexeme(self, addr: int = 0) -> str:
        symbol = self._get_symbol(addr=addr)
        return symbol.lexeme if symbol else None

    def is_symbol_current_scope(self, addr: int = 0, lexeme: str = '') -> int:
        symbol = self._get_symbol(addr=addr, lexeme=lexeme)
        return symbol.scope == len(self._scope_stack) if symbol else None

    def get_address(self) -> int:
        addr = self._current_address
        self._current_address += self._step
        return addr

    def add_symbol(self, lexeme: str = '', _type: str = '', line: int = 0, category: str = 'var', force: bool = False) -> Symbol:
        symbol = self._get_symbol(lexeme)
        if force or not symbol:
            symbol = Symbol(lexeme, self.get_address(), _type=_type, line=line, category=category,
                            scope=len(self._scope_stack))
            self._symbols.append(symbol)
            return symbol

    def set_pb_line(self, line: int) -> None:
        self._symbols[-1].pb_line = line

    def set_category(self, lexeme: str = None, addr: int = None, category: str = 'var'):
        symbol = self._get_symbol(lexeme=lexeme, addr=addr)
        symbol.category = category if symbol else None

    def set_args_cells(self, lexeme: str = None, addr: int = None, count: int = 0):
        symbol = self._get_symbol(lexeme=lexeme, addr=addr)
        symbol.args_cells = count if symbol else None

    def get_pb_line(self, lexeme: str = None, addr: int = None) -> int:
        symbol = self._get_symbol(lexeme=lexeme, addr=addr)
        return symbol.pb_line if symbol else None

    def inc_args(self):
        symbol = self._get_symbol(category='func')
        symbol.args_cells += 1
        print(symbol.lexeme, symbol.args_cells)

    def get_func_args_count(self, lexeme: str = None, addr: str = None) -> int:
        if lexeme:
            symbol = self._get_symbol(lexeme=lexeme)
        elif addr:
            symbol = self._get_symbol(addr=int(addr))
        else:
            symbol = self._get_symbol(category='func')
        return symbol.args_cells if symbol else None

    def kill_block(self, addr: str = None) -> None:
        for symbol in reversed(self._symbols):
            if symbol.address == addr:
                break
            symbol.alive = False

    def scope_push(self):
        self._scope_stack.append(len(self._symbols) - 1)

    def scope_pop(self):
        self._scope_stack.pop()

    def __str__(self) -> str:
        res = f'{"":<4}{"lexeme":<10} {"address":<10} {"PB_line":<10} {"category":<10}' + \
              f' {"args_cells":<10} {"type":<10} {"line":<10} {"alive":<10} {"scope":<10}\n'
        count = 0
        for symbol in self._symbols:
            res += f'{count:<3} {str(symbol)}' + '\n'
            count += 1
        return res

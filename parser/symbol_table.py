from typing import Iterator


class Symbol:
    def __init__(self, lexeme:str='', address:int=0, category:str='var', _type:str='', line:int=0) -> None:
        self._lexeme = lexeme
        self._address = address
        self._category = category # {func, var, param}
        self._args_cells = 0
        self._type = _type
        self._line = line
        self._pb_line = 0
        self._alive = True
    
    @property 
    def lexeme(self):
        return self._lexeme
    
    @property
    def address(self):
        return self._address

    @property
    def category(self):
        return self._category
    
    @property
    def args_cells(self):
        return self._args_cells
    
    @property
    def pb_line(self):
        return self._pb_line
    
    @property
    def alive(self):
        return self._alive
    
    @pb_line.setter
    def pb_line(self, val):
        self._pb_line = val
    
    @args_cells.setter
    def args_cells(self, val):
        self._args_cells = val
    
    @category.setter
    def category(self, val):
        self._category = val

    @alive.setter
    def alive(self,val):
        self._alive = val
        
    def __str__(self) -> str:
        return f'{self._lexeme:<10} {self._address:<10} {self._pb_line:<10} {self._category:<10} {self._args_cells:<10} {self._type:<10} {self._line:<10} {self._alive:<10}'

class SymbolTable:
    def __init__(self, start_address:int=100, step:int=4) -> None:
        self._current_address = start_address
        self._step = step
        self._symbols = list()
    
    @property
    def alive_symbols(self) -> Iterator:
        return filter(lambda s: s.alive, reversed(self._symbols))
    
    def _get_symbol(self, lexeme:str=None, addr:int=None, category:str=None) -> Symbol:
        for symbol in self.alive_symbols:
            if symbol.lexeme == lexeme:
                return symbol
            elif symbol.address == addr:
                return symbol
            elif symbol.category == category:
                return symbol
    
    def find_addr(self, lexeme:str='') -> int:
        symbol = self._get_symbol(lexeme=lexeme)
        return symbol.address if symbol else None
        
    def find_lexeme(self, addr:int=0) -> str:
        symbol = self._get_symbol(addr=addr)
        return symbol.lexeme if symbol else None
    
    def get_address(self) -> int:
        addr = self._current_address
        self._current_address += self._step
        return addr
    
    def add_symbol(self, lexeme:str='', _type:str='', line:int=0, category:str='var') -> Symbol:
        if not self.find_addr(lexeme):
            symbol = Symbol(lexeme, self.get_address(), _type=_type, line=line, category=category)
            self._symbols.append(symbol)
            return symbol
    
    def set_pb_line(self, line:int) -> None:
        self._symbols[-1].pb_line = line
    
    def set_param(self, lexeme:str=None, addr:int=None):
        self.set_category(lexeme=lexeme, addr=addr, category='param')
        self.inc_args(self._get_symbol(category='func'))
        
    def set_category(self, lexeme:str=None, addr:int=None, category:str='var'):
        symbol = self._get_symbol(lexeme=lexeme, addr=addr)
        symbol.category = category if symbol else None
    
    def set_args_cells(self, lexeme:str=None, addr:int=None, count:int=0):
        symbol = self._get_symbol(lexeme=lexeme, addr=addr)
        symbol.args_cells = count if symbol else None
    
    def get_pb_line(self, lexeme:str=None, addr:int=None) -> int:
        symbol = self._get_symbol(lexeme=lexeme, addr=addr)
        return symbol.pb_line if symbol else None
    
    def inc_args(self, symbol):
        symbol.args_cells += 1
    
    def get_func_args_count(self, lexeme:str=None, addr:str=None) -> int:
        if lexeme:
            symbol = self._get_symbol(lexeme=lexeme)
        elif addr:
            symbol = self._get_symbol(addr=addr)
        else:    
            symbol = self._get_symbol(category='func')
        return symbol.args_cells if symbol else None
    
    def kill_block(self, addr:str=None) -> None:
        for symbol in reversed(self._symbols):
            if symbol.address == addr:
                break
            symbol.alive = False
    
    def __str__(self) -> str:
        res = f'{"":<4}{"lexeme":<10} {"address":<10} {"PB_line":<10} {"category":<10} {"args_cells":<10} {"type":<10} {"line":<10} {"alive":<10}\n'
        count = 0
        for symbol in self._symbols:
            res += f'{count:<3} {str(symbol)}' + '\n'
            count += 1 
        return res
            

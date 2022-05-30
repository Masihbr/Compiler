class Symbol:
    def __init__(self, lexeme:str='', address:int=0, _type:str='', line:int=0) -> None:
        self._lexeme = lexeme
        self._address = address
        self._type = _type
        self._line = line
    
    @property 
    def lexeme(self):
        return self._lexeme
    
    @property
    def address(self):
        return self._address

    def __str__(self) -> str:
        return f'{self._lexeme:<10} {self._address:<10} {self._type:<10} {self._line:<10}'

class SymbolTable:
    def __init__(self, start_address:int=100, step:int=4) -> None:
        self._current_address = start_address
        self._step = step
        self._symbols = list()
    
    def find_addr(self, lexeme:str=''):
        for symbol in self._symbols:
            if symbol.lexeme == lexeme:
                return symbol.address 

    def find_lexeme(self, addr:int=0):
        for symbol in self._symbols:
            if symbol.address == addr:
                return symbol.lexeme
    
    def get_address(self):
        addr = self._current_address
        self._current_address += self._step
        return addr
    
    def add_symbol(self, lexeme:str='', _type:str='', line:int=0):
        if not self.find_addr(lexeme):
            self._symbols.append(Symbol(lexeme, self.get_address(), _type, line))
    
    def __str__(self) -> str:
        res = f'{"":<4}{"lexeme":<10} {"address":<10} {"type":<10} {"line":<10}\n'
        count = 0
        for symbol in self._symbols:
            res += f'{count:<3} {str(symbol)}' + '\n'
            count += 1 
        return res
            

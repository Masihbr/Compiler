class Symbol:
    def __init__(self, lexeme:str='', address:int=0, _type:str='', line:int=0) -> None:
        self.lexeme = lexeme
        self.address = address
        self._type = _type
        self.line = line
    

    def __str__(self) -> str:
        return f'{self.lexeme:<10} {self.address:<10} {self._type:<10} {self.line:<10}'

class SymbolTable:
    def __init__(self) -> None:
        self.current_address = 100
        self.symbols = list()
    
    def find_addr(self, lexeme:str=''):
        for symbol in self.symbols:
            if symbol.lexeme == lexeme:
                return symbol 

    def get_address(self):
        addr = self.current_address
        self.current_address += 4
        return addr
    
    def add_symbol(self, lexeme:str='', _type:str='', line:int=0):
        if not self.find_addr(lexeme):
            self.symbols.append(Symbol(lexeme, self.get_address(), _type, line))
    
    def __str__(self) -> str:
        res = f'{"":<4}{"lexeme":<10} {"address":<10} {"type":<10} {"line":<10}\n'
        count = 0
        for symbol in self.symbols:
            res += f'{count:<3} {str(symbol)}' + '\n'
            count += 1 
        return res
            

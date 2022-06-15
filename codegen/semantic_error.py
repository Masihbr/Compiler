import enum

#lineno: Semantic Error! main function not found
#lineno: Semantic Error! 'ID' is not defined appropriately
#lineno: Semantic Error! Mismatch in numbers of arguments of 'ID'
#lineno: Semantic Error! No 'while' found for 'break'
#lineno: Semantic Error! No 'while' found for 'continue'
#lineno: Semantic Error! Void type in operands
#lineno: Semantic Error! Function 'ID' has already been defined with this number of arguments

class SemanticError(enum.Enum):
    MAIN_MISSING = 0
    ID_NOT_DEFINED = 1
    ARGS_MISMATCH = 2
    BREAK_MISSING_WHILE = 3
    CONTINUE_MISSING_WHILE = 4
    VOID_OPERAND = 5
    OVERLOADING = 6

class SemanticErrorHandler:
    def __init__(self) -> None:
        self.semantic_errors = list()
        
    def add(self, error:int, lineno:int, id:str=''):
        error_massage = f'#{lineno} : Semantic Error! '
        if error == SemanticError.MAIN_MISSING:
            error_massage += f'main function not found.'
        if error == SemanticError.ID_NOT_DEFINED:
            error_massage += f'\'{id}\' is not defined appropriately.'
        if error == SemanticError.ARGS_MISMATCH:
            error_massage += f'Mismatch in numbers of arguments of \'{id}\'.'
        if error == SemanticError.BREAK_MISSING_WHILE:
            error_massage += f'No \'while\' found for \'break\'.'
        if error == SemanticError.CONTINUE_MISSING_WHILE:
            error_massage += f'No \'while\' found for \'continue\'.'
        if error == SemanticError.VOID_OPERAND:
            error_massage += f'Void type in operands.'
        if error == SemanticError.OVERLOADING:
            error_massage += f'Function \'{id}\' has already been defined with this number of arguments.'
        self.semantic_errors.append(error_massage)
        
    def get_errors_str(self) -> str:
        return '\n'.join(self.semantic_errors)
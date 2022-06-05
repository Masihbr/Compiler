class ProgramBlock:
    THREE_OPERAND = {'ADD', 'MULT', 'SUB', 'EQ', 'LT'}
    TWO_OPERAND = {'ASSIGN', 'JPF'}
    ONE_OPERAND = {'PRINT', 'JP'}

    def __init__(self) -> None:
        self.codes = list()

    def code(self, action: str = '', *args) -> str:
        args_len = len(args)
        if action == '':
            return f'( , , , )'
        if args_len > 3:
            raise Exception('Wrong inputs')
        if action in self.THREE_OPERAND and args_len == 3:
            return f'({action}, {args[0]}, {args[1]}, {args[2]})'
        elif action in self.TWO_OPERAND and args_len == 2:
            return f'({action}, {args[0]}, {args[1]}, )'
        elif action in self.ONE_OPERAND and args_len == 1:
            return f'({action}, {args[0]}, , )'
        else:
            raise Exception(
                f'Number of inputs {args_len} does not match action {action}')

    def str_program_block(self) -> str:
        line = 0
        res = ''
        for code in self.codes:
            res += f'{line}\t{code}\n'
            line += 1
        return res

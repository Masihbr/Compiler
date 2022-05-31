from codegen.program_block import ProgramBlock
from codegen.temp_manager import TempManager


class Stack:
    def __init__(self, program_block: ProgramBlock, temp_manager: TempManager, sp: int = 500, point: int = 8000, step: int = 4) -> None:
        self._program_block = program_block
        self._temp_manager = temp_manager
        self._sp = sp
        self._pointer = 0
        self._step = step
        self.program_block.append(self.code('ASSIGN', f'#{point}', self._sp))

    @property
    def program_block(self):
        return self._program_block.codes

    @property
    def pb_len(self):
        return len(self.program_block)

    @property
    def code(self):
        return self._program_block.code

    def push(self, value) -> None:
        temp = self._temp_manager.get_temp()
        self.program_block.append(
            self.code('ADD', {self._sp}, f'#{self._pointer}', temp))
        self.program_block.append(self.code('ASSIGN', value, f'@{temp}'))
        self._pointer += self._step

    def pop(self) -> int:
        temp1, temp2 = self._temp_manager.get_temp(), self._temp_manager.get_temp()
        if self._pointer > 0:
            self._pointer -= self._step
            self.program_block.append(
                self.code('ADD', {self._sp}, f'#{self._pointer}', temp1))
            self.program_block.append(self.code('ASSIGN', f'@{temp1}', temp2))
            return temp2

    def access(self, offset: int) -> int:
        temp1, temp2 = self._temp_manager.get_temp(), self._temp_manager.get_temp()
        _pointer = self._pointer - offset * self._step
        self.program_block.append(
            self.code('ADD', {self._sp}, f'#{_pointer}', temp1))
        self.program_block.append(self.code('ASSIGN', f'@{temp1}', temp2))
        return temp2

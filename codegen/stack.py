from collections import deque

from codegen.program_block import ProgramBlock
from codegen.temp_manager import TempManager


class Stack:
    def __init__(
            self,
            program_block: ProgramBlock,
            temp_manager: TempManager,
            sp: int = 500,
            point: int = 8000,
            step: int = 4
    ) -> None:
        self._program_block = program_block
        self._temp_manager = temp_manager
        self._sp = sp
        self._start = point
        self._step = step
        self.shadow_stack = deque()
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

    @property
    def is_empty(self):
        return self._sp == self._start

    def push(self, value) -> None:
        self.shadow_stack.append(value)
        self.program_block.append(self.code('ASSIGN', value, f'@{self._sp}'))
        self.program_block.append(self.code('ADD', self._sp, f'#{self._step}', self._sp))
        self._start += self._step

    def pop(self) -> int:
        temp = self._temp_manager.get_temp()
        self.program_block.append(self.code('SUB', self._sp, f'#{self._step}', self._sp))
        self.program_block.append(self.code('ASSIGN', f'@{self._sp}', temp))
        self.shadow_stack.pop()
        return temp

    def pop_all(self) -> list:
        res = []
        while not self.is_empty:
            res.append(self.pop())
        return res

    def access(self, offset: int) -> int:
        temp1, temp2 = self._temp_manager.get_temp(), self._temp_manager.get_temp()
        self.program_block.append(self.code('SUB', self._sp, f'#{offset * self._step}', temp1))
        self.program_block.append(self.code('ASSIGN', f'@{temp1}', temp2))
        return temp2

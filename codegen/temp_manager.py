class TempManager:
    def __init__(self, start_address: int = 1500, step: int = 4):
        self.var_temp = start_address
        self.arr_temp = start_address * 2
        self._step = step

    def get_temp(self):
        addr = self.var_temp
        self.var_temp += self._step
        return addr

    def get_arr_temp(self):
        addr = self.arr_temp
        self.arr_temp += self._step
        return addr

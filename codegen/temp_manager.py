class TempManager:
    def __init__(self, start_address:int=1500, step:int=4):
        self.current_temp = start_address
        self._step = step

    def get_temp(self):
        addr = self.current_temp
        self.current_temp += self._step
        return addr

    def get_arr_temp(self, arr_len):
        self.current_temp += self._step
        start_point = self.current_temp
        self.current_temp += self._step * (arr_len - 1)
        return start_point
class FileHandler:
    def __init__(self) -> None:
        self.buffer_size = 1024

    def read_all(self, address: str = "input", format: str = ".txt") -> str:
        try:
            with open(address + format, 'r') as file:
                return file.read()
        except IOError:
            return ""

    def write(self, address: str = "output", format: str = ".txt", string: str = "") -> bool:
        try:
            with open(address + format, "w") as file:
                file.write(string)
            return True
        except IOError:
            return False

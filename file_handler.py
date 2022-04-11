class FileHandler:
    def __init__(self) -> None:
        self.buffer_size = 32

    def read_chunks(self, filename: str = "input", format: str = ".txt"):
        with open(filename + format, "rb") as file:
            chunk = file.read(self.buffer_size)
            while chunk:
                yield chunk
                chunk = file.read(self.buffer_size)

    def read_all(self, filename: str = "input", format: str = ".txt") -> str:
        try:
            with open(filename + format, 'r') as file:
                return file.read()
        except IOError:
            return ""

    def write(self, filename: str = "output", format: str = ".txt", string: str = "") -> bool:
        try:
            with open(filename + format, "w") as file:
                file.write(string)
            return True
        except IOError:
            return False

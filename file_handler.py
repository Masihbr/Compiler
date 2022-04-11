def read_chunks(filename: str = "input", format: str = ".txt", buffer_size: int = 4096):
    with open(filename + format, "r") as file:
        chunk = file.read(buffer_size)
        while chunk:
            yield chunk
            chunk = file.read(buffer_size)

def read_all(filename: str = "input", format: str = ".txt") -> str:
    try:
        with open(filename + format, 'r') as file:
            return file.read()
    except IOError:
        return ""

def write_all(filename: str = "output", format: str = ".txt", string: str = "") -> bool:
    try:
        with open(filename + format, "w") as file:
            file.write(string)
        return True
    except IOError:
        return False

"""
Masih Beigi - 98101244
Ali Moroukian - 98106094
"""

from scanner import Scanner

if __name__ == '__main__':  
    scanner = Scanner()
    while True:
        token = scanner.get_next_token()
        if token is None:
            break

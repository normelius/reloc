"""
Reloc
@ 2020, Anton Normelius.
Simple file transfer package between client and server.
MIT License.
"""

# Imports
from reloc import Reloc

def main():
    server = Reloc()
    server.connect_server(mode = 'internal', host = 'localhost', port = 1750,
            def_path = '/users/antonnormelius/documents')
    server.receive()


if __name__ == '__main__':
    main()


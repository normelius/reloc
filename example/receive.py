# Author: norme
# Example code for server side.

from context import src

def main():
    server = src.reloc.Reloc()
    server.connect_server(mode = 'internal', host = 'localhost', port = 1750,
            def_path = '/users/antonnormelius/documents')
    server.receive()


if __name__ == '__main__':
    main()


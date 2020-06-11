# Author: norme
# Example code for server side.

import reloc

def main():
    server = reloc.Reloc()
    server.connect_server(mode = 'internal', host = 'localhost', port = 1750,
            def_path = '/users/antonnormelius/documents')
    server.receive()


if __name__ == '__main__':
    main()


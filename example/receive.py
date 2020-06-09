# Author: norme
# Example code for server side.

from context import src

def main():
    server = src.Trado()
    server.connect_server(mode = 'internal',
            port = 1337)
    server.add_path('users/antonnormelius/documents')
    print("Before receiving")
    server.receive()
    print("After receiving")


if __name__ == '__main__':
    main()


# Author: norme
# Example code for client side.

from context import src

def main():
    #host = '192.168.1.21'
    host = 'localhost'
    port = 1750
    filename = 'try_to_send_me'

    client = src.Reloc()
    client.connect_client(host = host, port = port)
    client.transmit(filename)

    client.disconnect()

if __name__ == '__main__':
    main()

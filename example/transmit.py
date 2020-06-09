# Author: norme
# Example code for client side.

from context import src

def main():
    host = '192.168.1.21'
    port = 1337
    client = src.Trado()
    client.connect_client(host, port)
    file_ = 'try_to_send_me'
    print("Before transmitting file")
    client.transmit(file_)
    print("After transmitting file")

if __name__ == '__main__':
    main()

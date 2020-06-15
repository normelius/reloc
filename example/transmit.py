"""
Reloc
@ 2020, Anton Normelius.
Simple file transfer package between client and server.
MIT License.
"""

from reloc import Reloc

def main():
    client = Reloc()

    filename = 'try_to_send_me'
    client.connect_client(host = 'localhost', port = 1750)
    client.transmit(filename)

    client.disconnect()

if __name__ == '__main__':
    main()

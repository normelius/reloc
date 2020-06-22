"""
Reloc
@ 2020, Anton Normelius.
Simple file transfer package between client and server.
MIT License.
"""

# Imports
import reloc

def main():
    folder = 'try_to_send_me'

    # Connecting to server on internal network.
    client = reloc.client(host = 'localhost', port = 1750)
    client.transmit(folder)

if __name__ == '__main__':
    main()

"""
Reloc
@ 2020, Anton Normelius.
Simple file transfer package between client and server.
MIT License.
"""

# Imports
import reloc

def main():

    # Connecting internally, i.e. in local network.
    server = reloc.server(mode = 'internal', host = 'localhost')
    server.receive()

if __name__ == '__main__':
    main()


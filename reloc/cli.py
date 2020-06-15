"""
Reloc
@ 2020, Anton Normelius.
Simple file transfer package between client and server.
MIT License.
"""

# Imports
import argparse

# Reloc imports
from client import Client

def cli_args():
    """
    Handle the arguments for reloc's command line interface.
    """

    parser = argparse.ArgumentParser(description 
            = "Handler for Reloc's command line interface.")
    parser.add_argument("mode", type = str)
    parser.add_argument("filename", type = str,
                    help = "Specify the file/folder to transmit.")
    parser.add_argument("--host", type = str,
                    help = "Specify the host that the server is connected to.")
    parser.add_argument("--port", type = int,
                    help = "Specify the port that the server is connected to.")
    args = parser.parse_args()
    
    if args.mode.lower() not in ['external', 'internal']:
        raise ValueError("Mode argument needs to be 'internal' " \
                "or 'external.'")

    if args.mode.lower() == 'external':
        if not args.host:
            raise ValueError("When using external mode, host needs to be " \
                    "specified with optional arguments.")

        if not args.port:
            raise ValueError("When using external mode, both host and port needs " \
                    "specified with optional arguments.")
        
    if args.mode.lower() == 'internal':
        if not args.host:
            args.host = 'localhost'

        if not args.port:
            # For now, use port 1750.
            args.port = 1750

    return args.filename, args.host, args.port

def cli_transmit():
    """
    Function to handle transmission of file/folder based
    on the users input arguments. 
    """
    filename, host, port = cli_args()
    client = Client(host = host, port = port)
    client.transmit(filename)
    client.disconnect()



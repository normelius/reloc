"""
Reloc
@ 2020, Anton Normelius.
Simple file transfer package between client and server.
MIT License.
"""

# Imports
import argparse
import sys

# Reloc imports
from .client import Client
from .server import Server

def cli_transmit():
    docs = dict()
    docs['main_parser'] = """usage: reloc <command>

Reloc commands that can be specified:

Positional:
    send [file]                 |   Send a file/folder to the server.
    start [external/internal]   |   Start a server.

Optional:
    [-h, --help]                |   Display help.
"""

    docs['start_parser'] = """usage: reloc start <command>

Reloc start commands that can be specified:

Positional:
        internal [--port, --host]   |   Start internal server for local network.
    or, external [host, --port]     |   Start external server for access over internet.
"""

    # Main parser
    parser = argparse.ArgumentParser()
    
    subparser = parser.add_subparsers(dest = 'main_parser')

    # Send parser
    parser_send = subparser.add_parser('send', add_help=False)
    parser_send.add_argument('file')
    parser_send.add_argument('--host', type = str)
    parser_send.add_argument('--port', type = int)
    
    # Start parser
    parser_start = subparser.add_parser('start')
    start_subparser = parser_start.add_subparsers(dest = 'start_parser')

    # Start parser --> Internal parser
    parser_internal = start_subparser.add_parser('internal')
    parser_internal.add_argument('--port', type = int)
    parser_internal.add_argument('--host', type = str)
    parser_internal.add_argument('--def_path', type = str)
    parser_internal.add_argument('--is_async', type = bool, default = False)
    parser_internal.add_argument('--use_log', type = bool, default = False)

    # Start parser --> External parser
    parser_external = start_subparser.add_parser('external')
    parser_external.add_argument('port', type = int)
    parser_external.add_argument('--host', type = str)
    parser_external.add_argument('--def_path', type = str)
    parser_external.add_argument('--is_async', type = bool, default = False)
    parser_external.add_argument('--use_log', type = bool, default = False)
    
    args = parser.parse_args()
    
    # Handle usage messages when no arguments are given
    # for the different parsers.
    if not args.main_parser:
        print(docs['main_parser'])
    
    if len(sys.argv) == 2 and args.main_parser == 'start':
        print(docs['start_parser'])

    # Handle different parsers here
    if args.main_parser == 'send':
        if not args.host:
            args.host = 'localhost'
        
        if not args.port:
            args.port = 1750
        
        client = Client(host = args.host, port = args.port)
        client.transmit(args.file)
        client.disconnect()
        return
    
    if args.main_parser == 'start':
        if args.start_parser == 'internal':
            server = Server(mode = 'internal')
            server.receive()
        
        elif args.start_parser == 'external':
            server = Server(mode = 'external',
                    host = args.host, port = args.port)
            server.receive()

        return



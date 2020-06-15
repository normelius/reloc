"""
Reloc
@ 2020, Anton Normelius.
Simple file transfer package between client and server.
MIT License.
"""

# Imports
import sys
import socket
import pathlib
import pickle
import time
import errno
import random
import ipify
import requests
import logging
import os
import datetime
from threading import Thread, active_count

# Package imports
from .util import Item

class Client():
    """
    Methods:
        connect_client: Connect to client by specifying
        the host and port that the server is connected to.

        disconnect: Disconnects from the socket
        that the client is connected to.

        ping: Serves as a transciever method for sending
        and receiving a simple message in order to check
        connection with the server, and the transfer of
        data.

        transmit: Call this method to actual send a folder/file
        to the server.

        __transmit_file: Private method that is used to handle
        file transmission. Can both be made on the main thread
        or not, based on if the user is running the client
        on the main thread or not, which is specified by the
        'is_async' param in the connect_client method.
    """
    def __init__(self, host, port, is_async = False,
            timeout = None):
        """
        Initiate connectiong with the socket.
        Params:
            host (str): Should be the same host, i.e. ip as the
            server is connected to.

            port (int): Should be the same port that the server
            is connected to.

            is_async (bool): Specify whether the client should send
            files on a separate thread. In case of transmission of
            large files, one might not want to occupy the
            main thread. Observe that generally file transfer
            is quite fast, so this shouldn't really be necessary.
            Default: False.

            timeout (float): Specify how long the client will
            try to connect to the server before it stops.
            Specify this as None will disable the timeout.
            Default: None.

        """
        self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        self.is_async = is_async

        if not isinstance(host, str):
            raise TypeError("Host specified on the wrong format, " \
                    "should be a str, i.e. '127.0.0.1'.")

        if not isinstance(port, int):
            raise TypeError("Port specified on the wrong format, " \
                    "should be an int, i.e. 1750.")

        if not isinstance(timeout, (type(None), int, float)) :
            raise TypeError("Timeout specified on the wrong format, " \
                    "should be an int or a float, i.e. 7 or 7.7")

        self.sock.settimeout(timeout)
        self.sock.connect((host, port))

    def disconnect(self):
        """
        Disconnects the socket in the client.
        """
        self.sock.close()

    def ping(self):
        """
        TODO
        """
        raise NotImplementedError

    def transmit(self, item_name):
        """
        Transmit a single file or folder. In case of folder,
        all folders and files included in the parent folder
        will be sent, excluding .dotfiles.

        Params:
            item_name (str): The file or folder to be sent
            to the server.
        """
        parent_path = pathlib.Path(item_name).absolute()
        transmit_data = list()

        # For now, dotfiles are not allowed to be transfered
        # since usual utf-8 codec can't decode the bytes.
        if parent_path.is_file() and str(parent_path.stem)[0] != '.':
            item = Item()
            item.path = parent_path.name
            item.type_ = "file"
            item.mtime = parent_path.stat().st_mtime
            item.size = parent_path.stat().st_size
            item.suffix = parent_path.suffix
            with open(str(parent_path), 'r') as f:
                item.content = f.read()

            transmit_data.append(item)

        elif parent_path.is_dir():

            # Add parent folder first
            item = Item()
            item.path = parent_path.stem
            item.type_ = "folder"
            transmit_data.append(item)

            # Iterate over all subfolders- and files
            for sub_item in parent_path.rglob("*"):
                item = Item()
                child_path = parent_path.stem / sub_item.relative_to(parent_path)
                item.path = child_path
                # If folder
                if sub_item.is_dir():
                    item.type_ = "folder"
                    transmit_data.append(item)

                # If file
                elif sub_item.is_file() and str(sub_item.stem)[0] != '.':
                    item.type_ = "file"
                    item.name = child_path.name
                    item.size = child_path.stat().st_size
                    with open(str(sub_item), 'r') as f:
                        item.content = f.read()

                    transmit_data.append(item)

        else:
            raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), item_name)

        # Data can be sent in a separate thread in order to avoid
        # blocking the main thread. This is optional.
        if self.is_async:
            client_thread = Thread(target = self._transmit_file, args =
            (transmit_data, parent_path))
            client_thread.start()

        else:
            self._transmit_file(transmit_data, parent_path)


    def _transmit_file(self, transmit_data, parent_path):
        """
        This method works on a separate thread, meaning
        the transmission of data doesn't occupy the main
        thread, making this non-blocking. As soon as the
        items has been sent, current thread will be closed.
        Params:
            transmit_data (list): The list with objects
            coming from method 'transmit'.

            parent_path (Path): A path to the folder/file
            that were sent. Used purely for visual purposes
            so we can print that the folder/files has been sent.
        """
        self.sock.sendall(pickle.dumps(transmit_data))

        if parent_path.is_dir():
            print("Successfully sent folder: {}".format(parent_path.name))

        elif parent_path.is_file():
            print("Successfully sent file: {}".format(parent_path.name))



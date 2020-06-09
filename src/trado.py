"""
@ 2020, Anton Normelius.
Simple file transfer library between client and server,
based on the socket library.
MIT License.
"""

# Imports
import sys
from pathlib import Path
import socket
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

class Trado():
    """
    Whole client and server is represented as a class.
    Methods:
        connect_client: Connect to client by specifying
        the host and port that the server is connected to.
            
        disconnect_client: Disconnects from the socket
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
    def __init__(self):
        self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        self.default_path = Path.home()
        self.log = None

    def connect_client(self, host, port, is_async = False):
        """
        Initiate connectiong with the socket.
        Params:
            host (str): e.g. 192.168.0.110
            port (int): e.g. 1337
        """
        self.is_async = is_async
        self._host = host
        self._port = port
        self.sock.connect((self._host, self._port))

    def disconnect_client(self):
        """
        Disconnects the used socket in the client.
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
        parent_path = Path(item_name).absolute()
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
                    with open(str(sub_item), 'r') as f:
                        item.content = f.read()

                    transmit_data.append(item)
                    
        else:
            raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), item_name)
        
        # Data should be sent in a separate thread in order to avoid 
        # blocking the main thread.
        if self.is_async:
            client_thread = Thread(target = self.__transmit_file, args =
            (transmit_data, parent_path))
            client_thread.start()

        else:
            self.__transmit_file(transmit_data, parent_path)

        
    def __transmit_file(self, transmit_data, parent_path):
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


    ## SERVER-SIDE CODE BELOW ##
    ## ______________________ ##
    def connect_server(self, mode = 'internal', port = None, 
            host = None, is_async = False, use_log = False):
        """
        Initiate connection with the server. By defualt, 
        connection is internal, meaning only local 
        file transfer will be possible.

        Params:
            mode (str): 'internal' or 'external'. By specifying internal,
            connection will be made over the local internet, meaning localhost
            will be used. By specifying 'external', connection can be made
            over the internet. In order for external connection to be possible
            the used port will need to be forward in the router.
            Observe that port forwarding exposes the server to the internet
            and should be used with caution.
            Default: internal.

            port (bool): Specify port that the server vill connect to.
            If param mode is specified as 'internal', standard port 1750
            will be used, if param mode is 'external', an error
            will be raised if no port is specified since it is required
            that the port is forwarded in advance.
            Default: None.

            host (str): The ip adress that the server will connect to.
            If param mode is 'internal', the primary host will automatically
            be the local ip in the network. If that ip isn't retrieved,
            standard host '127.0.0.1', i.e. 'localhost' will be used.
            If param mode is specified as 'external', both the external
            ipv4/ipv6 will be recived. For now, ipv4 will be used. Need
            to handle this better in the future.
            Default: None.

            is_async (bool): If need to run the server separate from 
            the main thread, and making it non-blocking. Since the
            file transfer is quite fast, this shouldn't really be 
            necessary. However, when transfering quite large 
            files (greater than 1 gb size), this might be necessary
            if other computations should be done at the same time.
            Observe that this only applies to the actual receiving
            of stream data. The actual connecting of the server, i.e.
            'connect_server' still executes on the main thread.
            Defualt: False.

            use_log (bool): Specify whether or not to use logging
            for the server.
            Defualt: False.
        """

        self.is_async = is_async
        self.use_log = use_log
        
        if self.use_log:
            self.__update_log('info', 'Starting server.')

        if mode.lower() == 'internal':
            host = self.__get_internal_ip()
            if not port:
                port = 1750

            if not isinstance(port, int):
                raise ValueError("Port specified on the wrong format, " \
                    "should be an int.")

            print("Observe that file transfer will only " \
                    "work on your local network, \n" \
                    "since the server started with internal host.")
            
            if self.use_log:
                self.__update_log('info', 'Server starting locally.')

        elif mode.lower() == 'external':
            if not port:
                raise ValueError("Need to specify an open port " \
                        "for external connection to be possible")

            if not isinstance(port, int):
                raise ValueError("Port specified on the wrong format, " \
                    "should be an int.")

            if not host:
                ips = self.__get_external_ip()
                host = ips['ipv4']
            
            if self.use_log:
                self.__update_log('info', 'Server starting externally.')
        
        self.sock.setsockopt(socket.SOL_SOCKET,
                socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.listen(10)
        
        print("Server connected to host: {}".format(host))
        print("Server connected to port: {}".format(port))
        print("Saving files to path: ".format(self.default_path))
        if self.use_log:
            self.__update_log('info', 'Server started on host {}, port {}.'.format(host, port))

    def __update_log(self, log_type, msg):
        """
        Handle updates to logs for the server.
        Multiple types of messages is written to 
        the logs in order to easier see that 
        correct files and folders has been transfered.
        Exceptions will be stored as well.

        Params:
            log_type (str): Specify the type of event that
            will be logged. Can be 'info' and 'exception' for now.

            msg (str): Message to be written to the log.
        """
        folder = Path('logs')
        if not folder.exists():
            os.makedirs(folder)
            
        date_today = Path(str(datetime.datetime.today().date()))
        log_path = Path(str(folder / date_today) + '.log')
            
        if not self.log:
            self.log = logging.getLogger(__name__) 
            self.log.setLevel(logging.INFO)
            handler = logging.FileHandler(log_path)
            formatter = logging.Formatter('%(asctime)s : %(levelname)s' \
                    ': %(name)s : %(message)s')
            handler.setFormatter(formatter)
            self.log.addHandler(handler)
            
        if not log_path.exists():
            # Create new handler
            new_handler = logging.FileHandler(log_path, 'a')
            new_formatter = logging.Formatter('%(asctime)s : %(levelname)s' \
                    ': %(name)s : %(message)s')
            new_handler.setFormatter(new_formatter)
                
            # Get logger and remove all old handlers
            logger = logging.getLogger()
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
            
            # Add new handler
            logger.addHandler(new_handler)

        if log_type == 'info':
            self.log.info(msg)

        elif log_type == 'exception':
            self.log.exception(msg)


    def add_path(self, new_path):
        """
        Let user specify default path for saving files and folders.
        If specified path doesn't exist, error will be raised.

        Params:
            new_path (str): Specify the default path for files and folders
            to be written to, e.g. /users/antonnormelius/documents.
            If specified path doesn't exist, error will be raised.
        """
        if new_path[0] != '/':
            new_path = '/' + new_path

        new_path = Path(new_path).absolute()
        if not new_path.exists():
            raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), str(new_path))

        self.default_path = new_path

    def __portscan(self, host):
        """
        TODO
        """
        open_ports = []
        for port in range(440, 450):
            try:
                self.sock.connect((host, port))
                open_ports.append(port)

            except:
                continue

        return open_ports
    
    def __get_external_ip(self):
        """
        Get external ip of the server. Utilizing ipify
        to retrieve both external ipv4 and ipv6.
        """
        ips = dict()
        ips['ipv4'] = requests.get('https://api.ipify.org').text
        ips['ipv6'] = requests.get('https://api6.ipify.org').text
        if self.use_log:
            self.__update_log('info', 'External ipv4 {} and ipv6 {} received'.format(
                ips['ipv4'], ipv['ipv6']))
        return ips

    def __get_internal_ip(self):
        """
        Get internal ip of the server, if specific ip is not found,
        standard localhost, i.e. 127.0.0.1, will be used.
        """
        host_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        try:
            # Try to get internal host.
            host_socket.connect(('10.255.255.255', 1))
            host = host_socket.getsockname()[0]
            if self.use_log:
                self.__update_log('info', 'Internal ip {} received.'.format(host))

        except:
            # If internal host could not be retrieved,
            # use standardized localhost, i.e. 127.0.0.1.
            host = '127.0.0.1'
            if self.use_log:
                self.__update_log('exception', 'Could not retrieve internal ip, standardised' \
                    ' ip {} is used'.format(host))

        host_socket.close()
        return host

    def receive(self):
        if self.is_async:
            self.server_thread = Thread(target = self.__receive_file)
            self.server_thread.start()

        else:
            self.__receive_file()

    def __receive_file(self):
        """
        Start to continuously listening for incoming 
        data stream from the client. The data contains 
        list of objects, either representing a single file
        or a whole folder structure with multiple folders/files.
        In case of receiving a folder, all items in the folder
        will be saved.
        """
        with self.sock:
            while True:
                conn, adr = self.sock.accept()
                with conn:
                    print("Connected by client: {}".format(adr))
                    if self.use_log:
                        self.__update_log('info', 'Connected by client {} on port {}.'.format(
                            adr[0], adr[1]))
                    byte = list()
                    while True:
                        partial = conn.recv(2**16)
                        if len(partial) <= 0:
                            break
                        
                        # Appending the partial data to list is a lot
                        # faster than concatenate byte strings.
                        byte.append(partial)

                    if byte:
                        data = pickle.loads(b''.join(byte))
                        for item in data:
                            path = self.default_path / item.path
                            if item.type_ == "folder":
                                if not path.exists():
                                    os.makedirs(path)
                                    if self.use_log:
                                        self.__update_log('info', 'Created folder on path {}.'.format(
                                            path))
                            
                            elif item.type_ == "file":
                                with open(path, 'w') as f:
                                    f.write(item.content)

                                if self.use_log: 
                                    self.__update_log('info', 'Saved file "{}" on path {}.'.format(
                                        item.name, path))
                                


class Item():
    """
    Class to contain a single item,
    which is represented as a file or folder.
    """
    def __init__(self):
        self.name = None
        self.path = None
        self.content = None
        self.type_ = None
        self.size = None
        self.mtime = None
        self.suffix = None




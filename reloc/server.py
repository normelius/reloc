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

class Server():
    """
    Methods:
        _update_log: Private method to update information to the log.

        add_path: Let's the user add it's own default path for where
        the receiving files will be saved. The home folder serves 
        as the standardized default path.

        _port_scan: Private method to handle portscanning to find
        open ports. This is not yet implemented (and not sure if it will be).

        _get_external_ip: Private method to get the external ip
        of the computer that starts the server. Useful such that the user
        doesn't have to specify the external ip.

        _get_internal_ip: Private method to get the internal ip of the computer.

        receive: Starts the listening process and calls _receive_file accordingly.
        The user calls this method the will either run on the main thread, or
        on a separate thread, depending on whether is_async is true.

        _receive_file: Private method that handles the receiving of incoming
        data streams.
    """
    def __init__(self, mode = 'internal', port = None,
            host = None, def_path = None,
            is_async = False, use_log = False):
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

            def_path (str): Specify the default path for files and folders
            to be written to, e.g. /users/antonnormelius/documents.
            If specified path doesn't exist, error will be raised.
            Default: None (i.e. home folder will be used).

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
        self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        self.is_async = is_async
        self.use_log = use_log
        self.log = None

        # If default_path isn't specified, use the home directory as
        # the default path.
        if not def_path:
            self.def_path = pathlib.Path.home()

        else:
            if not isinstance(def_path, str):
                raise TypeError("Wrong format on default path, should " \
                        "be a str, i.e. /users/antonnormelius/documents")

            if not pathlib.Path(def_path).absolute().exists():
                raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), str(def_path))

            self.def_path = pathlib.Path(def_path)

        if self.use_log:
            self._update_log('info', 'Starting server.')

        # Check internal mode handling
        if mode.lower() == 'internal':
            if host and not isinstance(host, str):
                raise TypeError("Host specified on the wrong format, " \
                        "should be a str.")
            if not host:
                # Might need to change this. CLI won't work with internal command
                # when internal ip is used. Might be better to user localhost or
                # 127.0.0.1.
                host = 'localhost'

            if port and not isinstance(port, int):
                raise ValueError("Port specified on the wrong format, " \
                    "should be an int.")

            if not port:
                # For now, always use same port.
                port = 1750

            if self.use_log:
                self._update_log('info', 'Server starting locally.')

        # Check external mode handling
        elif mode.lower() == 'external':
            if host and not isinstance(host, str):
                raise TypeError("Host specified on the wrong format, " \
                        "should be a str.")

            if host and host.lower() in ['localhost', '127.0.0.1']:
                raise ValueError("Localhost not allowed since server is " \
                        "starting in external mode, need to specify the external ip.")

            if not host:
                host = self._get_internal_ip()

            if not port:
                raise ValueError("Need to specify an open port " \
                        "for external connection to be possible")

            if not isinstance(port, int):
                raise ValueError("Port specified on the wrong format, " \
                    "should be an int.")

            if self.use_log:
                self._update_log('info', 'Server starting externally.')

        self.sock.setsockopt(socket.SOL_SOCKET,
                socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.listen(10)

        print("Server connected to host: {}".format(host))
        print("Server connected to port: {}".format(port))
        if mode.lower() == 'external':
            ips = self._get_external_ip()
            external_host = ips['ipv4']
            print("External host: {}".format(external_host))

        if self.use_log:
            self._update_log('info', 'Server started on host {}, port {}.'.format(host, port))

    def _update_log(self, log_type, msg):
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
        folder = pathlib.Path('logs')
        if not folder.exists():
            os.makedirs(folder)

        if not self.log:
            self.log = logging.getLogger(__name__)
            self.log.setLevel(logging.INFO)
            handler = logging.FileHandler(log_path)
            formatter = logging.Formatter('%(asctime)s : %(levelname)s' \
                    ': %(name)s : %(message)s')
            handler.setFormatter(formatter)
            self.log.addHandler(handler)

        date_today = pathlib.Path(str(datetime.datetime.today().date()))
        log_path = pathlib.Path(str(folder / date_today) + '.log')
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
        """
        if new_path[0] != '/':
            new_path = '/' + new_path

        new_path = pathlib.Path(new_path).absolute()
        if not new_path.exists():
            raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), str(new_path))

        self.default_path = new_path


    def _portscan(self, host):
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

    def _get_external_ip(self):
        """
        Get external ip of the server. Utilizing ipify
        to retrieve both external ipv4 and ipv6.
        """
        ips = dict()
        ips['ipv4'] = requests.get('https://api.ipify.org').text
        ips['ipv6'] = requests.get('https://api6.ipify.org').text
        if self.use_log:
            self._update_log('info', 'External ipv4 {} and ipv6 {} received'.format(
                ips['ipv4'], ipv['ipv6']))
        return ips

    def _get_internal_ip(self):
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
                self._update_log('info', 'Internal ip {} received.'.format(host))

        except:
            # If internal host could not be retrieved,
            # use standardized localhost, i.e. 127.0.0.1.
            host = '127.0.0.1'
            if self.use_log:
                self._update_log('exception', 'Could not retrieve internal ip, standardised' \
                    ' ip {} is used'.format(host))

        host_socket.close()
        return host

    def receive(self):
        if self.is_async:
            self.server_thread = Thread(target = self._receive_file)
            self.server_thread.start()

        else:
            self._receive_file()

    def _receive_file(self):
        """
        Start to continuously listening for incoming
        data stream from the client. The data contains
        list of objects, either representing a single file
        or a whole folder structure with multiple folders/files.
        In case of receiving a folder, all items in the folder
        will be saved.
        """
        print("Saving files to path: {}".format(self.def_path))
        with self.sock:
            while True:
                connection, adr = self.sock.accept()
                with connection:
                    print("Connected by client {} on port {}.".format(adr[0], adr[1]))
                    if self.use_log:
                        self._update_log('info', 'Connected by client {} on port {}.'.format(
                            adr[0], adr[1]))

                    byte_data = list()
                    while True:
                        partial = connection.recv(2**12)
                        if not partial:
                            break

                        # Appending the partial data to list is a lot
                        # faster than concatenate byte strings.
                        byte_data.append(partial)
                    
                    if byte_data:
                        data = pickle.loads(b''.join(byte_data))
                        for item in data:
                            path = self.def_path / item.path
                            if item.type_ == "folder":
                                if not path.exists():
                                    os.makedirs(path)
                                    if self.use_log:
                                        self._update_log('info', 'Created folder on path {}.'.format(
                                            path))

                            elif item.type_ == "file":
                                with open(path, 'wb') as f:
                                    f.write(item.content)

                                if self.use_log:
                                    self._update_log('info', 'Saved file "{}" on path {}.'.format(
                                        item.name, path))



